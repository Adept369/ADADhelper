# Enhanced Dockerfile for Caelum ADHD Assistant
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for wkhtmltopdf and PDF rendering
RUN apt-get update && apt-get install -y \
    curl \
    wkhtmltopdf \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxrender1 \
    libxext6 \
    libx11-6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Initialize the database and start the Flask app with Gunicorn
CMD ["sh", "-c", "python init_system.py && gunicorn run:app --bind 0.0.0.0:5000 --timeout 120"]
