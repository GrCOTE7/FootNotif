[CmdletBinding()]
param(
    [switch]$NoStart,
    [switch]$NoFront
)

# Encodage UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$venvPath = Join-Path $PSScriptRoot ".venv"

# Si le shell est déjà dans ce venv, on le désactive avant suppression/recréation.
if ($env:VIRTUAL_ENV -and ($env:VIRTUAL_ENV -eq $venvPath)) {
    if (Get-Command deactivate -ErrorAction SilentlyContinue) {
        deactivate
        Write-Host "Venv courant désactivé pour permettre sa recréation."
    }
}

# Ferme les processus qui utilisent des binaires du .venv (ex: app.py déjà lancé).
$lockingProcesses = Get-CimInstance Win32_Process | Where-Object {
    ($_.ExecutablePath -and $_.ExecutablePath.StartsWith($venvPath, [System.StringComparison]::OrdinalIgnoreCase)) -or
    ($_.CommandLine -and $_.CommandLine -match [regex]::Escape("$venvPath\\Scripts"))
}

if ($lockingProcesses) {
    Write-Host "Arrêt des processus qui verrouillent .venv..."
    foreach ($proc in $lockingProcesses) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
            Write-Host " - Processus arrêté: PID $($proc.ProcessId)"
        }
        catch {
            Write-Host " - [WARN] Impossible d'arrêter PID $($proc.ProcessId): $($_.Exception.Message)"
        }
    }
    Start-Sleep -Milliseconds 800
}

# Suppression silencieuse des dossiers (reset)
Write-Host "----------------------------------------"
Write-Host "Reset..."
Write-Host "----------------------------------------"
$old = $ProgressPreference
$ProgressPreference = 'SilentlyContinue'
Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force football-admin\node_modules -ErrorAction SilentlyContinue
$ProgressPreference = $old

if (Test-Path .venv) {
    Write-Host "[ERREUR] ❌ Impossible de supprimer .venv (fichiers encore verrouillés)."
    Write-Host "Ferme les terminaux/API front encore ouverts puis relance le script."
    exit 1
}

Write-Host "[OK] ✅ Réinitialisation terminée.`n"


Write-Host "----------------------------------------"
Write-Host "(Re)-Installation des dépendances..."
Write-Host "----------------------------------------"
# Création du venv avec un Python bootstrap hors .venv
$created = $false
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
    & $pyLauncher.Source -3 -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        $created = $true
    }
}
if (-not $created) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd -and -not $pythonCmd.Source.StartsWith($venvPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        & $pythonCmd.Source -m venv .venv
        if ($LASTEXITCODE -eq 0) {
            $created = $true
        }
    }
}
if (!(Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[ERREUR] ❌ Échec de création du venv. Lance le script hors .venv actif ou installe le launcher 'py'."
    exit 1
}

# Activation du venv dans le shell parent (dot sourcing)
. .\.venv\Scripts\Activate.ps1

# 🔥 Étape demandée : mise à jour de pip
Write-Host "`nMise à jour de pip..."
python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] Échec de mise à jour de pip."
    exit 1
}
Write-Host "[OK] ✅ pip mis à jour.`n"

# Installation des dépendances
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] ❌ Installation échouée."
    exit 1
}
Write-Host "[OK] ✅ Dépendances installées.`n"

# Création du dossier logs si absent
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path logs | Out-Null
}

# Installation des dépendances Node si nécessaire
$nodePath = $null
if (Test-Path "football-admin\package.json") {
    Write-Host "package.json détecté dans football-admin — installation..."
    $nodePath = "football-admin"
}
elseif (Test-Path "package.json") {
    Write-Host "package.json détecté à la racine — installation..."
    $nodePath = "."
}
if ($nodePath) {
    if ($nodePath -ne ".") { Push-Location $nodePath }
    npm install
    if ($nodePath -ne ".") { Pop-Location }
    Write-Host "[OK] ✅ Installation Node complète.`n"
}
else {
    Write-Host "Aucun package.json trouvé — rien à installer."
}
$installTask = Join-Path $PSScriptRoot "installTask.ps1"

if (Test-Path $installTask) {
    Write-Host "Running installTask.ps1..."
    . $installTask
}
else {
    Write-Host "installTask.ps1 not found"
    exit 1
}

Write-Host "[OK] ✅ Installation complète.`n"


$startScript = Join-Path $PSScriptRoot "start.ps1"

if (-not $NoStart) {
    if (Test-Path $startScript) {
        Write-Host "Lancement automatique de start.ps1..."

        # Construction dynamique des arguments
        $args = @()
        if ($NoFront) { $args += "-NoFront" }

        & $startScript @args
    }
    else {
        Write-Host "[WARN] start.ps1 introuvable, démarrage ignoré."
    }
}
else {
    Write-Host "[INFO] 🚫 Démarrage automatique désactivé (-NoStart)."
}
