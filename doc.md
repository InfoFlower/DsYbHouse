# HOUSIFY — Documentation technique

> Dernière mise à jour : avril 2026
> → [README](readme.md) | [Roadmap](roadmap.md)

---

## Architecture générale

HOUSIFY est une application web locale (homelab) construite autour de trois axes :

1. **Collecte** : récupération de vidéos depuis YouTube et de métadonnées depuis Discogs
2. **Stockage** : base SQLite avec schéma évolutif (colonnes ajoutées dynamiquement)
3. **Consultation** : interface web avec filtres, tri et vues grille/liste

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  YouTube API v3 │────▶│                  │────▶│  housify.db │
└─────────────────┘     │  flask_server.py │     │   (SQLite)  │
┌─────────────────┐     │   + Z_methods    │     └──────┬──────┘
│   Discogs API   │────▶│                  │            │
└─────────────────┘     └────────┬─────────┘            │
                                 │                      │
                        ┌────────▼─────────┐            │
                        │   Frontend web   │◀───────────┘
                        │  (HTML/CSS/JS)   │
                        └──────────────────┘
```

---

## Stack technique

| Couche | Technologie |
|---|---|
| Serveur | Python / Flask |
| Base de données | SQLite (`data/housify.db`) |
| APIs externes | YouTube Data API v3, Discogs API |
| Frontend | HTML / CSS / JS vanilla |
| Dépendances Python | `requests`, `tqdm`, `pandas`, `numpy`, `psutil`, `python-dotenv` |

---

## Point d'entrée : `flask_server.py`

Serveur Flask exposant les fichiers statiques et les endpoints API.

### Routes

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Page d'accueil |
| GET | `/web/<path>` | Fichiers statiques du frontend |
| GET | `/api/get_videos/<search>/<type>/<need_db>` | Récupère les vidéos YouTube. `type` = `USER` ou `PLAYLIST`. Si `need_db=true`, écrit en base |
| GET | `/api/see_database/` | Retourne tout le contenu de la table `music` |
| GET | `/api/consolidated_data/send_musicdiscg/` | Retourne la vue consolidée `musicdisg` (music + discogs + rating) |

### Configuration

Via fichier `.env` à la racine :

| Variable | Description |
|---|---|
| `WD` | Chemin absolu du projet |
| `YTB_API` | Clé API YouTube Data v3 |

---

## Fichiers racine utilitaires

| Fichier | Description |
|---|---|
| `test.py` | Script de test : exporte la vue `musicdisg` en JSON (`musicdisg.json`) |
| `output.csv` | Export CSV de la requête de consolidation |
| `modified_data.csv` | Export de débogage généré par `DB_Manager` lors de corrections de structure |
| `musicdisg.json` | Snapshot JSON de la vue consolidée |
| `log.txt` | Sortie de `Z_methods.py` |

---

## Documentation par dossier

| Dossier | Documentation | Description |
|---|---|---|
| `src/` | [src/_doc.md](src/_doc.md) | Code source Python : APIs, BDD, normalisation JSON, orchestration |
| `data/` | [data/doc.md](data/doc.md) | Base de données, scripts SQL, schéma MPD |
| `web/` | [web/doc.md](web/doc.md) | Interface web : pages, filtres, interactions API |

---

## Flux de données principaux

### 1. Import YouTube → base locale

```
Utilisateur (web/retreive_videos)
  → GET /api/get_videos/<search>/<type>/true
    → High_level_API.get_all_videos()
      → pagination YouTube → PlaylistDataNormalizer
        → db_manager.write_db(table='music', delete_on='playlistId')
```

### 2. Enrichissement Discogs (recherche)

```
Z_methods.consolidate_discoggs_data()
  → Pour chaque titre dans music (où Discogged IS NULL) :
    → Mid_level_API.get_release_id(titre)
      → SingleLayerDataNormalizer (ajoute etag comme clé étrangère)
    → Marque Discogged='Y' dans music
  → Insère les résultats dans table discogs
```

### 3. Import détaillé Discogs (multi-tables)

```
Z_methods.import_discord_database()
  → Pour chaque id dans discogs (absent de discogs_main) :
    → Mid_level_API.get_all_data(id)
      → JSON_Global_Multilayer.walker()
        → DB_JsonHandler.create_table() + insert_data()
          → Tables : discogs_main, artists, tracklist, rating, formats, labels…
```

### 4. Consultation consolidée

```
Utilisateur (web/view_musicdisg)
  → GET /api/consolidated_data/send_musicdiscg/
    → db_manager.read_db(table='musicdisg')
      → Vue SQL : music ⟕ discogs ⟕ discogs_main ⟕ rating
```

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
