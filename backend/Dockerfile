# ==============================================================================
# LamiGo Backend Dockerfile
# ==============================================================================

# --- Base Image ---
# Using the 'slim' version of Python 3.13 to keep the container lightweight 
# while still having the necessary Debian core to run the API.
FROM python:3.13-slim

# --- Environment Variables ---
# PYTHONDONTWRITEBYTECODE: Prevents Python from cluttering the container with .pyc files
# PYTHONUNBUFFERED: Forces Python to output logs immediately so they show up in Docker instantly
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore

# --- Working Directory ---
WORKDIR /app

# --- System Dependencies ---
# 'build-essential' and 'libpq-dev' are required by Debian to compile PostgreSQL 
# drivers (psycopg) from source if a pre-compiled binary isn't available.
# The 'rm -rf' line at the end cleans up the apt cache to keep the image size small.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Python Dependencies ---
# We copy ONLY the requirements.txt first. This utilizes Docker's "Layer Caching".
# If you change a Python file, Docker skips this step. It only re-runs pip install 
# if you actually add a new package to requirements.txt.
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# Now we copy the rest of your LamiGo code into the container.
COPY . .

# --- Port Exposure ---
EXPOSE 8000

# --- Execution Command ---
# Runs the FastAPI server via Uvicorn. 
# The '--reload' flag works perfectly with the 'volumes' mapping in our docker-compose.yml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]