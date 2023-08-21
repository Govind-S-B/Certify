# Use the official Alpine Python image as the base
FROM python:3.9-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY api_server.py /app/

# Run the Flask application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--certfile", "/app/ssl/cert.pem", "--keyfile", "/app/ssl/key.pem", "api_server:app"]