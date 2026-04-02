# Тестовое задание Лабаротария Касперского

API для частотного анализа текстовых файлов с лемматизацией русских слов.

## Стек

- FastAPI
- Celery
- Redis
- pymorphy3 (лемматизация) python>=3.1
- openpyxl (Excel)

## Запуск
```python
python -m uvicorn app.main:app
celery -A app.celery_app worker --loglevel=info --pool=solo
redis-server.exe (port 6379)
```
При необходимости сгенерированные тестовые данные находятся в папке test_data/
