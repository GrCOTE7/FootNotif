#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p logs
logFile="logs/job.log"

PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

{
  echo "=============================="
  echo "$(date '+%Y-%m-%d %H:%M:%S') Starting job"
} >> "$logFile"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

apiUrl="http://127.0.0.1:$API_PORT"
pythonBin="$(pwd)/.venv/bin/python"

status="$(curl -s -o /dev/null -w "%{http_code}" "$apiUrl/health" || true)"

if [ "$status" != "200" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') API not running, starting..." >> "$logFile"

  if pgrep -f "127.0.0.1:$API_PORT" >/dev/null 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') API process seems already starting, waiting..." >> "$logFile"
  else
    nohup "$pythonBin" app.py >> "$logFile" 2>&1 &
  fi

  tries=0
  while true; do
    sleep 1
    tries=$((tries+1))
    status="$(curl -s -o /dev/null -w "%{http_code}" "$apiUrl/health" || true)"
    if [ "$status" = "200" ]; then
      echo "$(date '+%Y-%m-%d %H:%M:%S') API started successfully" >> "$logFile"
      break
    fi
    if [ "$tries" -ge 20 ]; then
      echo "$(date '+%Y-%m-%d %H:%M:%S') API failed to start" >> "$logFile"
      exit 1
    fi
  done
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') Sending notifications" >> "$logFile"
curl -s -X POST "$apiUrl/notifications/send" >> "$logFile"
echo >> "$logFile"
echo "$(date '+%Y-%m-%d %H:%M:%S') Job finished" >> "$logFile"
