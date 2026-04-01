import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/file_processing"))
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    TASK_TTL = int(os.getenv("TASK_TTL", "3600"))  

config = Config()
config.TEMP_DIR.mkdir(parents=True, exist_ok=True)