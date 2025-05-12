# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server script
COPY server.py .

# Expose the SSE port
EXPOSE 9090

# Run the server with Python
CMD ["python", "server.py"]
