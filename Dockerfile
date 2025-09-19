FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY test_backend.py .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "backend/app.py"]