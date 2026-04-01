import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import aiofiles
import logging

from app.models import TaskResponse, TaskResult, TaskStatus
from app.task_manager import task_manager
from app.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Word Frequency Report API",
    description="Тестовое задание backend-разработка"
)

@app.post("/public/report/export", response_model=TaskResponse)
async def create_report(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Загрузить текстовый файл для анализа
    
    Возвращает task_id для отслеживания статуса
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    
    try:
        temp_dir = config.TEMP_DIR
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file_path = temp_dir / f"input_{file.filename}"
        
        async with aiofiles.open(temp_file_path, "wb") as out:
            content = await file.read()
            await out.write(content)
        
        logger.info(f"File saved: {temp_file_path}, size: {len(content)} bytes")
        
        task_id = task_manager.create_task(temp_file_path, file.filename)
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING
        )
        
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/public/report/export/{task_id}", response_model=TaskResult)
async def get_report_status(task_id: str):
    """
    Получить статус обработки задачи
    """
    try:
        status_info = task_manager.get_task_status(task_id)
        
        return TaskResult(
            task_id=task_id,
            status=status_info["status"],
            file_url=f"/public/report/download/{task_id}" if status_info["status"] == TaskStatus.SUCCESS else None,
            error=status_info.get("error"),
            progress=status_info.get("progress")
        )
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/public/report/download/{task_id}")
async def download_report(task_id: str):
    """
    Скачать отчет
    """
    try:
        output_path = task_manager.get_task_result(task_id)
        
        if not output_path or not output_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=output_path,
            filename=f"frequency_report_{task_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/public/report/export/{task_id}")
async def cancel_report(task_id: str):
    """
    Отменить обработку задачи
    """
    try:
        success = task_manager.revoke_task(task_id, terminate=True)
        
        if success:
            return {"status": "cancelled", "task_id": task_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to cancel task")
            
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Проверка состояния сервиса
    """
    try:
        from app.celery_app import celery_app
        celery_app.control.ping(timeout=1.0)
        
        return {"status": "healthy", "celery": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}