#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
rootDir="$(pwd)"

chmod +x "$rootDir/install.sh" 2>/dev/null || true
chmod +x "$rootDir/installTask.sh" 2>/dev/null || true
chmod +x "$rootDir/runJob.sh" 2>/dev/null || true

if [ ! -f "$rootDir/.env" ]; then
  echo "Warning: $rootDir/.env not found"
fi

if [ -d "$rootDir/football-admin" ] && [ ! -f "$rootDir/football-admin/.env" ]; then
  echo "Warning: $rootDir/football-admin/.env not found"
fi

echo "Checking Node..."

if ! command -v npm >/dev/null 2>&1; then
  echo "Node not found, installing..."
  if command -v apt >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y nodejs npm
  else
    echo "Unsupported package manager. Install Node manually."
    exit 1
  fi
fi

echo "Checking Python..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python not found, installing..."
  if command -v apt >/dev/null 2>&1; then
    sudo apt install -y python3 python3-venv python3-pip
  else
    echo "Unsupported package manager. Install Python manually."
    exit 1
  fi
fi

mkdir -p logs

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

venvPython="$rootDir/.venv/bin/python"

if [ ! -f "$venvPython" ]; then
  echo "Virtual environment Python not found"
  exit 1
fi

"$venvPython" -m pip install --upgrade pip

if [ -f "$rootDir/requirements.txt" ]; then
  "$venvPython" -m pip install -r "$rootDir/requirements.txt"
fi

if [ -f "$rootDir/football-admin/package.json" ]; then
  cd "$rootDir/football-admin"
  npm install
  cd "$rootDir"
elif [ -f "$rootDir/package.json" ]; then
  npm install
fi

if [ -f "$rootDir/installTask.sh" ]; then
  chmod +x "$rootDir/installTask.sh"
  "$rootDir/installTask.sh"
else
  echo "installTask.sh not found"
  exit 1
fi

echo "Installation complete"