# Nom de la tâche
$taskName = "FootballNotifier"

# Emplacement du script à exécuter
$jobPath = Join-Path $PSScriptRoot "runJob.bat"

# Vérifie si la tâche existe déjà
$taskExists = schtasks /query /tn $taskName 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Task already exists"
}
else {
    Write-Host "Creating task..."
    schtasks /create `
        /sc daily `
        /st 00:00 `
        /tn $taskName `
        /tr "`"$jobPath`"" `
        /f
}
