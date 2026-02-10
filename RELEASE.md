# Release Process

This document describes how to create a new release and publish the Docker image.

## Creating a Release

When you're ready to publish a new version:

1. **Create and push a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Or create a release through GitHub UI:**
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Choose or create a new tag (e.g., `v1.0.0`)
   - Add release title and description
   - Click "Publish release"

## What Happens Next

The GitHub Action workflow (`.github/workflows/docker-publish.yml`) will automatically:
1. Build the Docker image
2. Tag it with multiple versions:
   - `ghcr.io/ihudak/otlp_histogram:v1.0.0` (full version)
   - `ghcr.io/ihudak/otlp_histogram:v1.0` (major.minor)
   - `ghcr.io/ihudak/otlp_histogram:v1` (major only)
   - `ghcr.io/ihudak/otlp_histogram:latest` (if on main branch)
3. Push to GitHub Container Registry (ghcr.io)

## Version Tag Format

Use semantic versioning: `vMAJOR.MINOR.PATCH`

Examples:
- `v0.0.1` - Initial development
- `v1.0.0` - First stable release
- `v1.1.0` - New feature added
- `v1.1.1` - Bug fix

## Using the Published Image

After the workflow completes, users can pull and run your image:

```bash
docker run -e DT_ENDPOINT="https://..." \
           -e DT_API_TOKEN="..." \
           -e INSECURE_SSL="true" \
           ghcr.io/ihudak/otlp_histogram:v1.0.0
```

## Viewing Published Packages

Published images are visible at:
`https://github.com/ihudak/otlp_histogram/pkgs/container/otlp_histogram`
