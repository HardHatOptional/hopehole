FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure environment variables can be loaded
RUN pip install --no-cache-dir python-dotenv

# Use unbuffered Python output
ENV PYTHONUNBUFFERED=1

# Default entrypoint
CMD ["python", "PyPIT.py"]