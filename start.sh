#!/usr/bin/env bash
# Start script for Render deployment

set -e

echo "🚀 Starting FastAPI application..."
echo "📍 Host: 0.0.0.0"
echo "🔌 Port: ${PORT:-10000}"

cd Backend
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}" --no-access-log
