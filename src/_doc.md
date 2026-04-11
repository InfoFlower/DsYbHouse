# src/ — Documentation technique

> Code source Python : APIs, gestion de la base de données, normalisation JSON, orchestration.

---

## Vue d'ensemble

Ce dossier contient toute la logique métier de HOUSIFY. Il s'organise en quatre couches :

| Couche | Fichiers | Rôle |
|---|---|---|
| APIs externes | `API_Base.py`, `API_Youtube.py`, `API_Discogs.py` | Communication avec YouTube Data API v3 et Discogs API |
| Base de données | `DB_Manager.py`, `DB_JsonHandler.py` | CRUD SQLite, création dynamique de tables |
| Normalisation JSON | `JSON_Basic.py`, `JSON_Youtube_Playlist.py`, `JSON_Discord_SingleLayer.py`, `JSON_Global_Multilayer.py` | Transformation des réponses API en données tabulaires |
| Orchestration | `Z_methods.py`, `AUTO_Head.py`, `AUTOMATE/` | Fonctions haut niveau, automatisation (en stand-by) |

---

## Modules

### `API_Base.py`

Classe `BaseAPI` : client HTTP générique. Effectue des requêtes GET avec injection automatique de la clé API dans les paramètres. Le paramètre `no_key=True` désactive l'injection (utilisé pour les endpoints publics Discogs).

- **Dépendances** : `requests`

### `API_Youtube.py`

Deux niveaux d'abstraction pour l'API YouTube Data v3 :

- `Mid_level_API` : accès unitaire (récupérer un channel ID, un playlist ID, les vidéos d'une playlist avec pagination)
- `High_level_API` : point d'entrée principal via `get_all_videos(search, type)` — accepte un username (`USER`) ou un ID de playlist (`PLAYLIST`), gère la pagination complète

- **Dépendances** : `API_Base.py`, `JSON_Youtube_Playlist.py`

### `API_Discogs.py`

Classe `Mid_level_API` pour l'API Discogs :

- `get_release_id(q)` : recherche une release par titre avec retry exponentiel (jusqu'à 3 tentatives)
- `get_all_data(release_id)` : récupère le JSON complet d'une release via l'endpoint public `/releases/<id>`

- **Dépendances** : `API_Base.py`

### `DB_Manager.py`

Classe `db_manager` : interface SQLite complète.

| Méthode | Description |
|---|---|
| `execute(sql_script)` | Exécution SQL libre |
| `write_db(header, data, ...)` | Écriture avec déduplication optionnelle (`delete_on`) |
| `insert_data(header, data, ...)` | Insertion avec support structure ligne (`row`) ou colonne (`column`) |
| `read_db(table_name, query)` | Lecture par nom de table ou requête SQL |
| `modifify_data(type, ...)` | Suppression ou mise à jour conditionnelle |
| `_ensure_columns(...)` | Ajout dynamique de colonnes manquantes via `ALTER TABLE` |

- **Dépendances** : `sqlite3`, `numpy`, `pandas`, `json`

### `DB_JsonHandler.py`

Classe `DB_JsonHandler` : persistance de données JSON multi-tables.

- `create_table(json_tables)` : crée dynamiquement les tables à partir d'un dictionnaire `{nom_table: {colonnes}}`
- `insert_data(json_tables, key)` : insère les données en mode colonne avec déduplication optionnelle

- **Dépendances** : `DB_Manager.py`

### `JSON_Basic.py`

Utilitaires simples : `save_json(data, filename)` et `load_json(filename)`.

### `JSON_Youtube_Playlist.py`

Classe `PlaylistDataNormalizer` : aplatit les réponses paginées YouTube en dictionnaire de listes. Filtre les vidéos privées/supprimées. Expose `get_header_and_data()` → `(header, list[tuple])`.

### `JSON_Discord_SingleLayer.py`

Classe `SingleLayerDataNormalizer` : normalise les résultats de recherche Discogs (structure mono-niveau). Supporte l'injection d'une clé étrangère (`added_key`/`added_value`) pour lier les releases aux vidéos via `etag`.

### `JSON_Global_Multilayer.py`

Classe `JSON_Global_Multilayer` : parcourt récursivement le JSON complet d'une release Discogs et le décompose en un graphe de tables relationnelles (`discogs_main` + tables enfants : `tracklist`, `formats`, `labels`, `artists`, `rating`, etc.).

- Méthode principale : `walker(json_data, table_name)` → `dict[table_name: {col: values}}`

### `Z_methods.py`

Fonctions d'orchestration haut niveau appelées par `flask_server.py` et en standalone :

| Fonction | Description |
|---|---|
| `request_videos_from_X(search, type)` | Récupère les vidéos YouTube via `High_level_API` |
| `consolidate_discoggs_data(max_results)` | Enrichit les titres `music` via la recherche Discogs puis marque `Discogged='Y'` |
| `import_discord_database()` | Pipeline complet : lit les IDs `discogs`, récupère les releases détaillées, normalise en multi-tables, insère via `DB_JsonHandler` |

---

## Sous-dossier `AUTOMATE/` (en stand-by)

Système d'automatisation des tâches — développement suspendu par choix de priorité (fonctionnalités utilisateur d'abord).

| Fichier | Description |
|---|---|
| `TASKS.py` | Classe `task` : exécution threadée avec suivi de statut (`PENDING`/`RUNNING`/`COMPLETED`/`ERROR`), mesure CPU/mémoire via `psutil` |
| `SCHEDULER.py` | Classe `scheduler` : file ordonnée avec dépendances et concurrence max — méthode `run()` non implémentée |
| `routes.csv` | Mapping tâche → route → description (vide) |
| `schedule.csv` | Configuration des planifications (vide) |

`AUTO_Head.py` (racine `src/`) référence un `RequestHandler` dans `AUTOMATE/TASKS` qui n'existe pas encore.