# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install any necessary dependencies
RUN pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
