#!/bin/sh
# entrypoint.sh

# Wait for n8n if N8N_URL and N8N_API_KEY are set
if [ -n "$N8N_URL" ] && [ -n "$N8N_API_KEY" ] && [ "$N8N_API_KEY" != "YOUR_N8N_API_KEY_HERE" ]; then
  echo "N8N_URL and N8N_API_KEY are set. Waiting for n8n at $N8N_URL to be healthy..."
  
  # Ensure N8N_URL does not have a trailing slash for concatenation
  N8N_BASE_URL=$(echo "$N8N_URL" | sed 's:/*$::')
  HEALTH_CHECK_URL="$N8N_BASE_URL/healthz"
  
  WAIT_TIMEOUT=120 # seconds (2 minutes)
  WAIT_INTERVAL=5  # seconds
  ELAPSED_TIME=0
  
  while [ $ELAPSED_TIME -lt $WAIT_TIMEOUT ]; do
    echo "Pinging n8n health check at $HEALTH_CHECK_URL..."
    # -s: silent, -f: fail fast (no output on error, return code non-zero), -L: follow redirects
    if curl -sfL "$HEALTH_CHECK_URL" > /dev/null; then
      echo "n8n is healthy!"
      break
    fi
    
    echo "n8n not healthy yet. Waiting $WAIT_INTERVAL seconds..."
    sleep $WAIT_INTERVAL
    ELAPSED_TIME=$((ELAPSED_TIME + WAIT_INTERVAL))
    
    if [ $ELAPSED_TIME -ge $WAIT_TIMEOUT ]; then
      echo "Timed out waiting for n8n. Continuing to start app, import might fail."
      break
    fi
  done
else
  if [ "$N8N_API_KEY" = "YOUR_N8N_API_KEY_HERE" ]; then
    echo "N8N_API_KEY is set to placeholder. Skipping n8n health check."
  else
    echo "N8N_URL or N8N_API_KEY not set. Skipping n8n health check."
  fi
fi

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 app:app
