FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OCR and vision
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY conf/ ./conf/

# Create necessary directories
RUN mkdir -p logs uploads

EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
