FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY send_histogram.py .

# Environment variables (can be overridden at runtime)
ENV DT_ENDPOINT=""
ENV DT_API_TOKEN=""
ENV INSECURE_SSL="false"
ENV INTERVAL="60"

# Run the application in loop mode with configurable interval
CMD sh -c "python send_histogram.py --loop --interval ${INTERVAL}"
