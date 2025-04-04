# Use a slim Python image as our base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port 5000 (our Flask app runs on 5000)
EXPOSE 5000

# Run the Flask app
CMD ["python", "run.py"]
