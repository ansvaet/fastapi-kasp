from celery import Task
from celery.utils.log import get_task_logger
from pathlib import Path
import traceback

from app.celery_app import celery_app
from app.process import process_file
from app.config import config

logger = get_task_logger(__name__)

@celery_app.task(
    bind=True,
    name="process_file",
    max_retries=3,
    default_retry_delay=60
)
def process_file_task(self, file_path: str, task_id: str) -> dict:

    try:
        input_path = Path(file_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        

        self.update_state(state="PROCESSING", meta={"progress": 0})
        
        output_path = config.TEMP_DIR / f"report_{task_id}.xlsx"

        process_file(input_path, output_path)
        
        return {
            "status": "SUCCESS",
            "output_file": str(output_path),
            "task_id": task_id
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Error processing file {task_id}: {e}")
        logger.error(traceback.format_exc())

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        raise

@celery_app.task(name="cleanup_temp_files")
def cleanup_temp_files(file_paths: list) -> None:

    for file_path in file_paths:
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Cleanup error {file_path}: {e}")