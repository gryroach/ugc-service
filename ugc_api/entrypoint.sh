#!/usr/bin/env bash

# Run the application.
if [ "$UGC_API_PRODUCTION" = "true" ]; then
  # https://fastapi.tiangolo.com/deployment/docker/#replication-number-of-processes
  echo "Запуск приложения в продакшн-режиме..."
  eval uv run fastapi run src/main.py --host 0.0.0.0 --port 8000
else
  echo "Запуск приложения в режиме разработки..."
  eval uv run fastapi dev src/main.py --host 0.0.0.0 --port 8000 --reload
fi
