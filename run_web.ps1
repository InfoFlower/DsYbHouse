Write-Host "Arrêt de tous les conteneurs..."
$runningContainers = docker ps -q
if ($runningContainers) {
    docker stop $runningContainers | Out-Null
    Write-Host "Tous les conteneurs ont été stoppés."
} else {
    Write-Host "Aucun conteneur en cours d'exécution."
}
Write-Host "Démarrage du service web..."
docker compose up -d web 
Write-Host "Service web en cours :"
docker compose ps web