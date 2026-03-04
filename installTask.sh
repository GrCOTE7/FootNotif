#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
jobPath="$(pwd)/runJob.sh"

line="0 0 * * * $jobPath"

( crontab -l 2>/dev/null | grep -F "$jobPath" ) >/dev/null 2>&1 && {
  echo "Cron already exists"
  exit 0
}

( crontab -l 2>/dev/null; echo "$line" ) | crontab -
echo "Cron installed: $line"