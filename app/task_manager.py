from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.tasks import process_file_task, cleanup_temp_files
from app.config import config
from app.models import TaskStatus

logger = logging.getLogger(__name__)

class CeleryTaskManager:

    
    def __init__(self):
        self.temp_files: Dict[str, Path] = {} 
    
    def create_task(self, file_path: Path, original_filename: str) -> str:
    
        task_id = None
        
        try:
            
            async_result = process_file_task.delay(
                str(file_path),
                None 
            )
            
            task_id = async_result.id
            self.temp_files[task_id] = file_path
            
            logger.info(f"Task created: {task_id} for file {original_filename}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            if file_path.exists():
                file_path.unlink()
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:

        try:
            async_result = AsyncResult(task_id, app=celery_app)
            
            status = async_result.state
            result_info = {
                "task_id": task_id,
                "status": status,
                "created_at": None,
                "completed_at": None,
                "progress": 0,
                "error": None,
                "output_file": None
            }
            
            if async_result.info:
                info = async_result.info
                if isinstance(info, dict):
                    result_info["progress"] = info.get("progress", 0)
                    result_info["error"] = info.get("error")
                    result_info["output_file"] = info.get("output_file")
                    result_info["message"] = info.get("message")
            

            if status == TaskStatus.SUCCESS:
                result = async_result.result
                if result and isinstance(result, dict):
                    result_info["output_file"] = result.get("output_file")
                    result_info["progress"] = 100

            elif status == TaskStatus.FAILURE:
                result_info["error"] = str(async_result.info) if async_result.info else "Unknown error"
            
            return result_info
            
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return {
                "task_id": task_id,
                "status": TaskStatus.FAILURE,
                "error": str(e)
            }
    
    def get_task_result(self, task_id: str) -> Optional[Path]:

        try:
            async_result = AsyncResult(task_id, app=celery_app)
            
            if async_result.state == TaskStatus.SUCCESS:
                result = async_result.result
                if result and isinstance(result, dict):
                    output_path = result.get("output_file")
                    if output_path:
                        return Path(output_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting task result: {e}")
            return None
    
    def cleanup_task(self, task_id: str) -> None:

        if task_id in self.temp_files:
            temp_file = self.temp_files[task_id]
            if temp_file.exists():
                temp_file.unlink()
                logger.info(f"Cleaned up temp file for task {task_id}")
            del self.temp_files[task_id]
        
        output_path = self.get_task_result(task_id)
        if output_path and output_path.exists():

            cleanup_temp_files.apply_async(
                args=[[str(output_path)]],
                countdown=300  # 5 минут
            )
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:

        try:
            async_result = AsyncResult(task_id, app=celery_app)
            async_result.revoke(terminate=terminate)
    
            self.cleanup_task(task_id)
            
            logger.info(f"Task {task_id} revoked")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking task {task_id}: {e}")
            return False

task_manager = CeleryTaskManager()