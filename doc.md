# HOUSIFY — Documentation synthétique

Application locale de gestion d'une vidéothèque musicale. Elle récupère les vidéos YouTube d'une chaîne ou d'une playlist, les stocke dans une base SQLite, et les enrichit avec des données Discogs.

---

## Stack

| Couche | Technologie |
|---|---|
| Serveur | Python / Flask |
| Base de données | SQLite (`data/housify.db`) |
| APIs externes | YouTube Data API v3, Discogs API |
| Frontend | HTML / CSS / JS vanilla |

---

## Lancement

```bash
# Créer un fichier .env à la racine :
# WD=<chemin absolu du projet>
# YTB_API=<clé API YouTube>

python flask_server.py
# → http://localhost:5000
```

---

## Routes Flask (`flask_server.py`)

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Page d'accueil |
| GET | `/web/<path>` | Fichiers statiques du frontend |
| GET | `/api/get_videos/<search>/<type>/<need_db>` | Récupère les vidéos YouTube. `type` = `USER` ou `PLAYLIST`. Si `need_db=true`, écrit en base. |
| GET | `/api/see_database/` | Retourne tout le contenu de la table `music` |
| GET | `/api_dev/consolidate_discogs_data/<max_results>/<overwrite_db>` | Enrichit les titres de la table `music` via l'API Discogs |
| GET | `/api_dev/consolidate_discogs_data/send_current_db/` | Retourne la table `discogs` |

---

## Structure du projet

```
flask_server.py          # point d'entrée
data/
  housify.db             # base SQLite
  sql/CREATE/            # scripts CREATE TABLE (music, discogs)
  sql/ETL_SCRIPTS/       # scripts de suppression/transformation
src/
  API_Base.py            # classe BaseAPI (requests HTTP génériques)
  API_Youtube.py         # Mid/High level API YouTube
  API_Discogs.py         # Mid level API Discogs
  DB_Manager.py          # CRUD SQLite (db_manager)
  JSON_Youtube_Playlist.py   # Normalisation JSON → table playlist
  JSON_Global_SingleLayer.py # Normalisation JSON → table à plat (Discogs)
  JSON_Basic.py          # utilitaire chargement JSON
  Z_methods.py           # fonctions haut niveau (request_videos_from_X, consolidate_discoggs_data)
  AUTOMATE/
    TASKS.py             # classe task (threading + suivi CPU/mémoire)
    SCHEDULER.py         # classe scheduler (WIP)
    routes.csv / schedule.csv
web/
  index/                 # page d'accueil
  retreive_videos/       # formulaire de récupération
  view_videos/           # visualisation des vidéos sauvegardées
```

---

## Modules `src`

### `API_Base.py`
Classe `BaseAPI` : effectue une requête GET authentifiée (`key` injectée dans les params).

### `API_Youtube.py`
- `Mid_level_API` : accès bas niveau (channel ID, playlist ID, vidéos paginées)
- `High_level_API.get_all_videos(search, type)` : point d'entrée principal ; accepte un username (`USER`) ou un ID de playlist (`PLAYLIST`)

### `API_Discogs.py`
- `Mid_level_API.get_release_id(q)` : recherche un titre dans la base Discogs avec retry exponentiel

### `DB_Manager.py`
- `db_manager(db_path)` : interface SQLite
  - `write_db(header, data, table_name, delete_on)` : crée la table si absente, supprime les doublons sur `delete_on`, insère les lignes
  - `read_db(table_name, query)` : lecture générique
  - `modifify_data(type, ...)` : `delete` ou `update` conditionnel

### `JSON_Youtube_Playlist.py`
`PlaylistDataNormalizer` : aplatit la réponse paginée YouTube en dictionnaire de listes → `get_header_and_data()`.

### `JSON_Global_SingleLayer.py`
`SingleLayerDataNormalizer` : générique, aplatit n'importe quelle liste `results` d'une réponse JSON mono-niveau (utilisé pour Discogs).

### `Z_methods.py`
- `request_videos_from_X(search, type)` : wrapper `High_level_API`
- `consolidate_discoggs_data(max_results, overwrite_db)` : lit les titres non enrichis depuis `music`, les interroge sur Discogs, stocke dans `discogs`, marque `Discogged='Y'`

### `AUTOMATE/`
- `task` : encapsule une fonction dans un thread, trace statut, durée, CPU, mémoire
- `scheduler` : planification ordonnée de tâches (WIP — `run()` non implémenté)

---

## Base de données

| Table | Alimentée par | Clé de déduplication |
|---|---|---|
| `music` | `/api/get_videos` | `playlistId` ou `videoOwnerChannelId` |
| `discogs` | `/api_dev/consolidate_discogs_data` | — |

Le schéma de chaque table est défini dans `data/sql/CREATE/CREATE_TABLE_<TABLE>.sql`.

---

## Variables d'environnement (`.env`)

| Variable | Usage |
|---|---|
| `WD` | Chemin absolu du projet (préfixe tous les accès fichiers) |
| `YTB_API` | Clé API YouTube Data v3 |
