# backend/Dockerfile

# 1. Base Image: Use a lightweight Python version matching your local setup
FROM python:3.10-slim

# 2. Environment Setup:
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures logs are flushed directly to terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Work Directory: All commands will run inside this folder in the container
WORKDIR /app

# 4. Install Dependencies:
# We copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Project Code:
# This copies everything from your local 'backend/' folder to '/app/' in the container
COPY . .

# 6. Run Command:
# Starts the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]c