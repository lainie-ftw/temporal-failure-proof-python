#!/bin/bash
set -e

echo "Starting Temporal development environment..."

# Activate Python virtual environment
export PATH=/workspace/venv/bin:$PATH
echo "Python virtual environment activated"

# Start Temporal server with retry logic
echo "Starting Temporal server..."
for i in {1..3}; do
  echo "Server start attempt $i..."
  nohup temporal server start-dev \
    --ui-port 8080 \
    --db-filename /workspace/clusterdata.db \
    --ip 0.0.0.0 > /workspace/temporal.log 2>&1 &
  
  sleep 30
  
  echo "Health check attempt $i: $(temporal operator cluster health --address 127.0.0.1:7233 2>&1 || true)"
  if temporal operator cluster health --address 127.0.0.1:7233 2>&1 | grep -q SERVING; then
    echo "Temporal server is healthy on attempt $i!"
    break
  else
    echo "Server not healthy, killing and retrying..."
    pkill -f "temporal server" || true
    sleep 5
    if [ $i -eq 3 ]; then
      echo "Failed to start Temporal server after 3 attempts"
      echo "Last 20 lines of temporal.log:"
      tail -n 20 /workspace/temporal.log
    fi
  fi
done

echo "Temporal server is running"
echo "  - Temporal UI: http://localhost:8080"
echo "  - Temporal gRPC: 127.0.0.1:7233"
echo ""
echo "Starting code-server..."
echo "  - Code Server: https://localhost:8443"
echo ""
echo "Setup complete! Virtual environment is at /workspace/venv"

# Start code-server in the foreground
exec /usr/bin/code-server \
  --host 0.0.0.0 \
  --port 8443 \
  --cert \
  --auth none \
  /workspace
