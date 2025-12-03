#!/usr/bin/env bash
set -e

PORT=${PORT:-8080}

# Install uvicorn/fastapi if not already installed (safe)
# (Optional: comment out if installer already installs dependencies)
pip install --no-cache-dir fastapi "uvicorn[standard]"

# Start uvicorn as PID 1 so it binds to $PORT for Koyeb health checks
exec uvicorn pyUltroid.asgi_app:app --host 0.0.0.0 --port "$PORT"
