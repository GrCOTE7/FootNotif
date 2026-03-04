#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p logs
logFile="logs/job.log"

{
  echo "=============================="
  echo "$(date '+%Y-%m-%d %H:%M:%S') Starting job"
} >> "$logFile"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

apiUrl="http://127.0.0.1:8000"

status="$(curl -s -o /dev/null -w "%{http_code}" "$apiUrl/health" || true)"

if [ "$status" != "200" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') API not running, starting..." >> "$logFile"
  nohup python3 app.py >> "$logFile" 2>&1 &
  tries=0
  while true; do
    sleep 1
    tries=$((tries+1))
    status="$(curl -s -o /dev/null -w "%{http_code}" "$apiUrl/health" || true)"
    if [ "$status" = "200" ]; then
      echo "$(date '+%Y-%m-%d %H:%M:%S') API started successfully" >> "$logFile"
      break
    fi
    if [ "$tries" -ge 10 ]; then
      echo "$(date '+%Y-%m-%d %H:%M:%S') API failed to start" >> "$logFile"
      exit 1
    fi
  done
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') Sending notifications" >> "$logFile"
curl -s "$apiUrl/notifications/send" >> "$logFile"
echo >> "$logFile"
echo "$(date '+%Y-%m-%d %H:%M:%S') Job finished" >> "$logFile"