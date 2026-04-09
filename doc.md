# HOUSIFY — Documentation synthétique

> Dernière mise à jour : avril 2026
> → [Roadmap](roadmap.md)

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
Classe `BaseAPI` : effectue une requête GET authentifiée (`key` injectée dans les params). Le paramètre `no_key=False` permet de désactiver l'injection de clé pour les endpoints publics (ex. détail d'une release Discogs).

### `API_Youtube.py`
- `Mid_level_API` : accès bas niveau (channel ID, playlist ID, vidéos paginées)
- `High_level_API.get_all_videos(search, type)` : point d'entrée principal ; accepte un username (`USER`) ou un ID de playlist (`PLAYLIST`)

### `API_Discogs.py`
- `Mid_level_API.get_release_id(q)` : recherche un titre dans la base Discogs avec retry exponentiel
- `Mid_level_API.get_all_data(release_id)` *(nouveau)* : récupère le JSON complet d'une release (`/releases/<id>`) sans clé API (`no_key=True`)

### `DB_Manager.py`
- `db_manager(db_path)` : interface SQLite — dépendances ajoutées : `numpy`, `pandas`
  - `execute(sql_script)` *(nouveau)* : exécution SQL libre
  - `_ensure_columns(conn, table_name, header)` *(nouveau)* : ajoute dynamiquement les colonnes manquantes via `ALTER TABLE` (schéma évolutif sans migration)
  - `write_db(header, data, table_name, delete_on, create, type_of_struct)` : `create` force la re-création de table ; `type_of_struct` (`'row'`/`'column'`) adapte la lecture des données
  - `insert_data(..., type_of_struct)` : gère les structures en colonnes ou en lignes, avec correction automatique des longueurs incohérentes et export CSV de débogage
  - `read_db(table_name, query)` : inchangé
  - `modifify_data(type, ..., type_of_struct)` : supporte `type_of_struct='column'` pour la déduplication sur données column-oriented

### `JSON_Youtube_Playlist.py`
`PlaylistDataNormalizer` : aplatit la réponse paginée YouTube en dictionnaire de listes → `get_header_and_data()`.

### `JSON_Discord_SingleLayer.py`
`SingleLayerDataNormalizer` : aplatit la liste `results` d'une réponse JSON Discogs mono-niveau. Accepte désormais un paramètre `added_key` / `added_value` pour injecter une clé étrangère (ex. `etag`) dans chaque ligne et assurer la liaison avec la table `music`.

> Remplace `JSON_Global_SingleLayer.py` pour l'usage Discogs.

### `JSON_Global_Multilayer.py` *(nouveau)*
`JSON_Global_Multilayer(identifier)` : parcourt récursivement un objet JSON complexe multi-niveaux et le décompose en un dictionnaire de tables relationnelles `{ table_name: {col: [values]} }`. Gère les listes de dicts (→ tables enfants), les dicts simples (→ sous-tables), et les scalaires. Utilisé pour modéliser le détail complet d'une release Discogs.

### `Z_methods.py`
- `request_videos_from_X(search, type)` : wrapper `High_level_API`
- `consolidate_discoggs_data(max_results, overwrite_db)` : lit les titres non enrichis depuis `music` (filtre `Discogged`), les interroge sur Discogs, injecte l'`etag` comme clé de liaison, stocke dans `discogs` via `SingleLayerDataNormalizer`, marque `Discogged='Y'`. Progression affichée via `tqdm`.
- `import_discord_database()` *(nouveau)* : pour chaque `id` distinct dans la table `discogs`, appelle `API_Discogs.get_all_data()` pour récupérer le détail complet de la release, le décompose via `JSON_Global_Multilayer`, crée dynamiquement les tables enfants via `DB_JsonHandler`, et insère les données. C'est le cœur de la base décisionnelle.

### `DB_JsonHandler.py` *(nouveau)*
`DB_JsonHandler` : couche d'accès spécialisée pour persister la sortie de `JSON_Global_Multilayer`.
- `create_table(json_tables)` : génère dynamiquement un `CREATE TABLE IF NOT EXISTS` pour chaque table du dict
- `insert_data(json_tables, key)` : insère en mode colonne (`type_of_struct='column'`) avec déduplication sur la clé fournie

### `AUTOMATE/`
- `task` : encapsule une fonction dans un thread, trace statut (`PENDING/RUNNING/COMPLETED/ERROR`), durée, CPU, mémoire
- `scheduler` : planification ordonnée de tâches (WIP — `run()` non implémenté)

---

## Base de données

| Table | Alimentée par | Clé de déduplication |
|---|---|---|
| `music` | `/api/get_videos` | `playlistId` ou `videoOwnerChannelId` |
| `discogs` | `Z_methods.consolidate_discoggs_data` | `id` (release Discogs) ; lié à `music` via `etag` |
| `discogs_main` + tables enfants | `Z_methods.import_discord_database` | `id_main` — tables générées dynamiquement par `JSON_Global_Multilayer` |

Le schéma de chaque table est défini dans `data/sql/CREATE/CREATE_TABLE_<TABLE>.sql`.

---

## Variables d'environnement (`.env`)

| Variable | Usage |
|---|---|
| `WD` | Chemin absolu du projet (préfixe tous les accès fichiers) |
| `YTB_API` | Clé API YouTube Data v3 |

---

## Structure `src` complète

```
API_Base.py
API_Youtube.py
API_Discogs.py
DB_Manager.py
DB_JsonHandler.py          ← nouveau
JSON_Youtube_Playlist.py
JSON_Discord_SingleLayer.py ← remplace JSON_Global_SingleLayer
JSON_Global_Multilayer.py  ← nouveau
JSON_Basic.py
Z_methods.py
AUTO_Head.py
AUTOMATE/
  TASKS.py
  SCHEDULER.py
  routes.csv
  schedule.csv
```
