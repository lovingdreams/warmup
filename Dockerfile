FROM selenium/standalone-chrome:latest

# Install Python and pip
USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the entire content of the current directory to /app in the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Change back to the selenium user (recommended by the selenium/standalone-chrome base image)
USER seluser
