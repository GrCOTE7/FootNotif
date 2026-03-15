#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"


jobPath="$(pwd)/runJob.sh"
logPath="$(pwd)/logs/cron.log"

chmod +x "$jobPath"

line="0 0 * * * $jobPath >> $logPath 2>&1"

if crontab -l 2>/dev/null | grep -F "$jobPath" >/dev/null; then
  echo "Cron already exists"
  exit 0
fi

( crontab -l 2>/dev/null; echo "$line" ) | crontab -

echo "Cron installed: $line"