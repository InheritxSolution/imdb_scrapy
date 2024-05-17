# Dockerfile

# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the image
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Scrapy project files into the image
COPY . .

# Define the entry point for the Docker container
ENTRYPOINT ["scrapy", "crawl", "imdb"]

