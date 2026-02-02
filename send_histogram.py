#!/usr/bin/env python3
"""
Send OTLP histogram metrics to Dynatrace Managed using OpenTelemetry SDK.

Environment variables:
  DT_ENDPOINT  -> e.g. https://<cluster>/e/<env-id>/api/v2/otlp
  DT_API_TOKEN -> Dynatrace API token with OTLP ingest permission

Usage:
  source venv/bin/activate
  export DT_ENDPOINT="https://your-cluster/e/your-env-id/api/v2/otlp"
  export DT_API_TOKEN="dt0c01...."
  
  # Send once and exit
  python send_histogram.py
  
  # Send continuously (once per minute)
  python send_histogram.py --loop
"""

import os
import sys
import time
import argparse
import random
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, AggregationTemporality
from opentelemetry.sdk.metrics._internal.instrument import Histogram
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource


def send_metrics(histogram):
    """Send a batch of histogram measurements with randomized values."""
    # Generate realistic random measurements
    measurements = [
        (random.uniform(10, 150), {"http.method": "GET", "http.status_code": 200}),
        (random.uniform(15, 120), {"http.method": "GET", "http.status_code": 200}),
        (random.uniform(20, 100), {"http.method": "POST", "http.status_code": 201}),
        (random.uniform(25, 180), {"http.method": "GET", "http.status_code": 200}),
        (random.uniform(30, 90), {"http.method": "PUT", "http.status_code": 200}),
    ]
    
    for value, attrs in measurements:
        histogram.record(value, attrs)
    
    return len(measurements)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Send OTLP histogram metrics to Dynatrace")
    parser.add_argument("--loop", action="store_true", help="Run continuously, sending metrics every minute")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds between sends (default: 60)")
    args = parser.parse_args()

    # Get configuration from environment
    endpoint = os.environ.get("DT_ENDPOINT", "").strip()
    token = os.environ.get("DT_API_TOKEN", "").strip()

    if not endpoint or not token:
        print("ERROR: Please set DT_ENDPOINT and DT_API_TOKEN.", file=sys.stderr)
        print("  DT_ENDPOINT example: https://<cluster>/e/<env-id>/api/v2/otlp", file=sys.stderr)
        print("  DT_API_TOKEN example: dt0c01...", file=sys.stderr)
        sys.exit(2)

    # Ensure endpoint ends with /v1/metrics for the exporter
    metrics_endpoint = endpoint.rstrip("/") + "/v1/metrics"

    # Configure OTLP exporter with protobuf over HTTP
    # Dynatrace requires DELTA temporality for histograms
    exporter = OTLPMetricExporter(
        endpoint=metrics_endpoint,
        headers={"Authorization": f"Api-Token {token}"},
        preferred_temporality={
            Histogram: AggregationTemporality.DELTA,
        },
    )

    # Create metric reader with immediate export (no periodic delay for demo)
    reader = PeriodicExportingMetricReader(
        exporter=exporter,
        export_interval_millis=5000,  # Export every 5 seconds
    )

    # Create MeterProvider with resource attributes
    resource = Resource.create({
        "service.name": "my-service",
        "deployment.environment": "prod",
    })

    provider = MeterProvider(
        resource=resource,
        metric_readers=[reader],
    )

    # Set global meter provider
    metrics.set_meter_provider(provider)

    # Create a meter
    meter = metrics.get_meter(
        name="example-meter",
        version="1.0.0",
    )

    # Create a histogram instrument
    histogram = meter.create_histogram(
        name="http.server.duration",
        description="HTTP request duration",
        unit="ms",
    )

    print(f"Sending histogram metrics to: {metrics_endpoint}")
    
    if args.loop:
        print(f"Running in loop mode (sending every {args.interval} seconds)")
        print("Press Ctrl+C to stop...\n")
        
        iteration = 0
        try:
            while True:
                iteration += 1
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"[{timestamp}] Iteration {iteration}: Recording measurements...")
                count = send_metrics(histogram)
                
                # Force flush to send metrics immediately
                provider.force_flush()
                
                print(f"[{timestamp}] ✓ Sent {count} measurements")
                
                # Wait for next iteration
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n\nStopping... Flushing final metrics...")
            provider.force_flush()
            provider.shutdown()
            print("Shutdown complete.")
    else:
        print("Recording sample measurements...")
        count = send_metrics(histogram)
        
        print("Measurements recorded. Waiting for export...")
        
        # Force flush to send metrics immediately
        provider.force_flush()
        
        print(f"✓ Metrics exported successfully! Sent {count} measurements.")
        print("\nNote: Check Dynatrace UI for the metric 'http.server.duration'")
        
        # Shutdown to ensure all metrics are sent
        provider.shutdown()


if __name__ == "__main__":
    main()
