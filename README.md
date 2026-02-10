# OTLP Histogram Metrics Sender for Dynatrace

This project sends OTLP histogram metrics to Dynatrace Managed using the OpenTelemetry SDK with protobuf format.

## Setup

1. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   
   Edit `.env` file with your Dynatrace credentials:
   ```
   DT_ENDPOINT=https://<cluster>/e/<env-id>/api/v2/otlp
   DT_API_TOKEN=dt0c01....
   ```
   
   **For local development with self-signed certificates:**
   ```
   DT_ENDPOINT=http://localhost:8080/api/v2/otlp
   # OR for HTTPS with untrusted certificate:
   DT_ENDPOINT=https://localhost:8443/api/v2/otlp
   INSECURE_SSL=true
   ```

## Usage

### Option 1: Use the helper script

**Send once and exit:**
```bash
./run.sh
```

**Run continuously (send every minute):**
```bash
./run.sh --loop
```

**Run continuously with custom interval:**
```bash
./run.sh --loop --interval 30  # Send every 30 seconds
```

### Option 2: Run manually
```bash
source venv/bin/activate
export $(cat .env | xargs)

# Send once
python send_histogram.py

# Send continuously (every minute)
python send_histogram.py --loop

# Custom interval (every 30 seconds)
python send_histogram.py --loop --interval 30
```

## How it works

- Uses OpenTelemetry SDK to create and send histogram metrics
- Sends data in **protobuf format** over HTTP (required by Dynatrace)
- Configures **DELTA temporality** for histograms (required by Dynatrace)
- Records sample HTTP request duration measurements
- Exports metrics to Dynatrace OTLP endpoint

## Key Features

- **Protobuf encoding**: Dynatrace requires protobuf, not JSON
- **DELTA temporality**: Dynatrace only accepts DELTA histograms, not CUMULATIVE
- **Proper resource attributes**: Sets service.name and deployment.environment
- **Custom attributes**: Each measurement includes http.method and http.status_code
- **HTTP/HTTPS support**: Works with both HTTP and HTTPS endpoints
- **Self-signed certificate support**: Use `INSECURE_SSL=true` for local development (disables SSL verification)

## Verify in Dynatrace

After running the script, check your Dynatrace environment for the metric:
- Metric name: `http.server.duration`
- Unit: `ms` (milliseconds)
- Dimensions: http.method, http.status_code, service.name, deployment.environment
