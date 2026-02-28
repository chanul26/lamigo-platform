# 1. Base Image: The highest-performance, lightweight version of your Mac's Python
FROM python:3.13-slim

# 2. Environment Configuration
# PYTHONDONTWRITEBYTECODE: Prevents Python from generating useless .pyc cache folders
# PYTHONUNBUFFERED: Forces logs to stream to your terminal instantly without delay
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set Working Directory
WORKDIR /app

# 4. Install Dependencies (The Caching Layer)
# We copy ONLY the requirements file first. 
# This means Docker will only re-download libraries if you actually change this file.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
# Copies all your LamiGo folders (app/, core/, etc.) into the container.
# Make sure your .dockerignore file is filtering out .env and .venv!
COPY . .

# 6. Standard Port Documentation
# EXPOSE doesn't actually publish the port, but it acts as vital documentation 
# for other developers and cloud providers that 8000 is the standard FastAPI port.
EXPOSE 8000

# 7. Start the Server
# Binds to 0.0.0.0 so it can receive traffic from outside the container walls
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]