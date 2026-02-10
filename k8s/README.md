# Kubernetes Deployment

This directory contains Kubernetes manifests to deploy the OTLP Histogram Sender application.

## Prerequisites

- A Kubernetes cluster
- `kubectl` configured to access your cluster
- Docker image published to GitHub Container Registry (see main README for releasing)

## Files

- `namespace.yaml` - Creates the `otlp-histogram` namespace
- `configmap.yaml` - Stores non-sensitive configuration (DT_ENDPOINT, INSECURE_SSL)
- `secret.yaml` - Stores sensitive data (DT_API_TOKEN)
- `deployment.yaml` - Deploys the application pod

## Quick Start

### 1. Update the configuration

**Edit `configmap.yaml`:**
```yaml
data:
  DT_ENDPOINT: "https://your-cluster.dynatrace.com/e/your-env-id/api/v2/otlp"
  INSECURE_SSL: "true"  # Set to "false" for production with valid certs
  INTERVAL: "60"        # Send metrics every 60 seconds
```

**Edit `secret.yaml`:**
```yaml
stringData:
  DT_API_TOKEN: "dt0c01.YOUR_ACTUAL_TOKEN_HERE"
```

**Edit `deployment.yaml`:**
```yaml
image: ghcr.io/ihudak/otlp_histogram:latest
```

### 2. Deploy to Kubernetes

Apply all manifests:
```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
```

Or apply all at once:
```bash
kubectl apply -f k8s/
```

### 3. Verify deployment

Check the pod status:
```bash
kubectl get pods -n otlp-histogram
```

View logs:
```bash
kubectl logs -n otlp-histogram deployment/otlp-histogram-sender -f
```

Check pod details:
```bash
kubectl describe pod -n otlp-histogram -l app=otlp-histogram-sender
```

## Updating Configuration

### Update ConfigMap (non-sensitive config)

```bash
kubectl edit configmap otlp-histogram-config -n otlp-histogram
```

Then restart the deployment:
```bash
kubectl rollout restart deployment/otlp-histogram-sender -n otlp-histogram
```

### Update Secret (API token)

```bash
kubectl edit secret otlp-histogram-secret -n otlp-histogram
```

Then restart the deployment:
```bash
kubectl rollout restart deployment/otlp-histogram-sender -n otlp-histogram
```

## Scaling

To run multiple instances (e.g., for higher data volume):
```bash
kubectl scale deployment/otlp-histogram-sender --replicas=3 -n otlp-histogram
```

## Uninstalling

Remove all resources:
```bash
kubectl delete -f k8s/
```

Or delete just the namespace (removes everything inside):
```bash
kubectl delete namespace otlp-histogram
```

## Troubleshooting

### Pod is in CrashLoopBackOff

Check logs:
```bash
kubectl logs -n otlp-histogram -l app=otlp-histogram-sender --tail=50
```

Common issues:
- Invalid API token (check secret)
- Wrong endpoint URL (check configmap)
- SSL certificate issues (set `INSECURE_SSL: "true"` for self-signed certs)

### Image pull errors

If using a private GitHub Container Registry, create an image pull secret:
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  -n otlp-histogram
```

Then add to `deployment.yaml`:
```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: ghcr-secret
```

## Resource Limits

Default resource limits:
- Memory: 64Mi request, 128Mi limit
- CPU: 100m request, 200m limit

Adjust these in `deployment.yaml` based on your needs.
