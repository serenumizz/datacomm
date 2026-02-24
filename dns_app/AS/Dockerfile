# Python Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy file requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Create file for persistent disk
RUN mkdir -p /app/data

# Expose UDP port 53533
EXPOSE 53533/udp

# Run Server
CMD ["python", "-u", "app.py"]
