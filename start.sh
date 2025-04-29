#!/bin/bash

# This command runs your FastAPI app using Gunicorn with Uvicorn workers
# Adjust "main:app" to the actual import path of your FastAPI app
#!/bin/bash
uvicorn main:app --host=0.0.0.0 --port=10000
