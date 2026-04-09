# HOUSIFY

Application homelab de gestion d'une vidéothèque musicale. Elle récupère les vidéos YouTube d'une chaîne ou d'une playlist, les stocke localement dans une base SQLite, et les enrichit avec les métadonnées de la base Discogs.

---

## Liens rapides

- [Documentation technique](doc.md) — architecture, modules, routes API, base de données
- [Roadmap](roadmap.md) — réalisations, chantiers en cours, plans futurs

---

## Démarrage rapide

**Prérequis :** Python 3.11+, pip

```bash
# 1. Installer les dépendances
pip install flask python-dotenv requests tqdm pandas numpy psutil

# 2. Créer un fichier .env à la racine
#    WD=C:/chemin/absolu/vers/HOUSIFY
#    YTB_API=<votre clé API YouTube Data v3>

# 3. Lancer le serveur
python flask_server.py
# → http://localhost:5000
```

---

## Fonctionnalités

| Page | Description |
|---|---|
| `/` | Accueil — navigation principale |
| Retrieve Videos | Récupère les vidéos d'une chaîne YouTube (`USER`) ou d'une playlist (`PLAYLIST`) et les sauvegarde en base |
| View Videos | Consulte la vidéothèque locale (vue grille ou liste) |

---

## Stack

| Couche | Technologie |
|---|---|
| Serveur | Python / Flask |
| Base de données | SQLite (`data/housify.db`) |
| APIs externes | YouTube Data API v3, Discogs API |
| Frontend | HTML / CSS / JS vanilla |
| Traitement données | pandas, numpy, tqdm |
