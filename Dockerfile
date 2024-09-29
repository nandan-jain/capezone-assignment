# Use the official Python base image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root --no-dev

# Copy the application code
COPY . .

# Expose the port the app will run on
EXPOSE 8000