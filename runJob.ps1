# Encodage UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# --- Initialisation ---------------------------------------------------------

Set-Location $PSScriptRoot

if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

$logFile = "logs/job.log"

function Log($msg) {
    $timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $logFile -Value "$timestamp $msg"
}

Log "==============================="
Log "Starting job"

# --- Chargement du .env -----------------------------------------------------

if (Test-Path ".env") {
    Get-Content ".env" |
        Where-Object { $_ -and -not $_.StartsWith("#") } |
        ForEach-Object {
            $parts = $_ -split "=", 2
            if ($parts.Count -eq 2) {
                Set-Item -Path "env:$($parts[0])" -Value $parts[1]
            }
        }
}

# --- Variables --------------------------------------------------------------

$pythonBin = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$apiUrl    = "http://127.0.0.1:$($env:API_PORT)"

# --- Vérification API -------------------------------------------------------

$status = (curl -s -o $null -w "%{http_code}" "$apiUrl/health")

if ($status -ne "200") {

    Log "API not running, starting..."

    # Vérifie si app.py tourne déjà
    $existing = Get-Process | Where-Object { $_.Path -like "*python*" -and $_.CommandLine -like "*app.py*" }

    if ($existing) {
        Log "API process seems already starting, waiting..."
    }
    else {
        # Lancement silencieux
        Start-Process -FilePath $pythonBin -ArgumentList "app.py" -WindowStyle Hidden -RedirectStandardOutput $logFile -RedirectStandardError $logFile
    }

    # Attente du démarrage
    $tries = 0
    while ($tries -lt 20) {
        Start-Sleep -Seconds 1
        $tries++

        $status = (curl -s -o $null -w "%{http_code}" "$apiUrl/health")

        if ($status -eq "200") {
            Log "API started successfully"
            break
        }
    }

    if ($status -ne "200") {
        Log "API failed to start"
        exit 1
    }
}

# --- Envoi des notifications ------------------------------------------------

Log "Sending notifications"
curl -s -X POST "$apiUrl/notifications/send" | Out-File -Append $logFile
Add-Content -Path $logFile -Value ""

# --- Arrêt de app.py --------------------------------------------------------

$procs = Get-Process | Where-Object { $_.Path -like "*python*" -and $_.CommandLine -like "*app.py*" }

foreach ($p in $procs) {
    Stop-Process -Id $p.Id -Force
}

Log "app.py stopped"
Log "Job finished"

exit 0
