# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY src src

# Expose the port the app runs on
EXPOSE 8080

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "src.main:create_application", "--host", "0.0.0.0", "--port", "8080", "--factory"]
