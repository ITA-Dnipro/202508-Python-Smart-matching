#!/bin/bash

echo "🚀 Starting Celery Worker..."
celery -A app.core.celery_app worker --beat --loglevel=info &

echo "🚀 Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload