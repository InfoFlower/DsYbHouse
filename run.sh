#!/bin/bash

echo "Arrêt de tous les conteneurs..."
running_containers=$(docker ps -q)
if [ -n "$running_containers" ]; then
    docker stop $running_containers > /dev/null
    echo "Tous les conteneurs ont été stoppés."
else
    echo "Aucun conteneur en cours d'exécution."
fi

echo "Démarrage du service db..."
docker compose up db -d

echo "Démarrage du service web..."
docker compose up web -d

echo "Service web en cours :"
docker compose ps web