#!/bin/bash

# This command runs your FastAPI app using Gunicorn with Uvicorn workers
# Adjust "main:app" to the actual import path of your FastAPI app

gunicorn main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:10000
