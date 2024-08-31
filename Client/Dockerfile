# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install Tkinter and other necessary dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    libffi-dev \
    libssl-dev \
    libbz2-dev \
    libsqlite3-dev \
    tk-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the client script
CMD ["python", "Advanced_Client.py"]
