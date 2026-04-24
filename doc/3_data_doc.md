# data/ — Documentation technique

> Données de l'application : base SQLite, fichiers bruts, scripts SQL.

---

## Vue d'ensemble

Ce dossier contient toutes les données persistées de HOUSIFY ainsi que les scripts SQL de création et de transformation.

| Élément | Description |
|---|---|
| `housify.db` | Base SQLite principale (non versionné) |
| `MUSIC.csv` | Export CSV de la table `music` |
| `raw_data.json` | Données brutes JSON (import initial) |
| `raw_info/` | JSON de releases Discogs individuelles (cache local) |
| `sql/` | Scripts SQL organisés par type : création, vues, ETL |

---

## Structure SQL

### `sql/CREATE_TABLES/`

Scripts `CREATE TABLE` pour chaque table de la base. Générés automatiquement par `py_utils/extract_tables.py` à partir du schéma existant de `housify.db`.

| Script | Table | Rôle |
|---|---|---|
| `CREATE_TABLE_MUSIC.sql` | `music` | Vidéos YouTube (PK: `etag`) |
| `CREATE_TABLE_DISCOGS.sql` | `discogs` | Résultats de recherche Discogs (PK: `id`, `etag`) |
| `CREATE_TABLE_DISCOGS_MAIN.sql` | `discogs_main` | Détails complets d'une release Discogs |
| `CREATE_TABLE_ARTISTS.sql` | `artists` | Artistes liés à une release |
| `CREATE_TABLE_TRACKLIST.sql` | `tracklist` | Pistes d'une release |
| `CREATE_TABLE_RATING.sql` | `rating` | Notes communautaires Discogs |
| `CREATE_TABLE_COMMUNITY.sql` | `community` | Stats communautaires (have/want) |
| `CREATE_TABLE_FORMATS.sql` | `formats` | Formats physiques (vinyle, CD…) |
| `CREATE_TABLE_LABELS.sql` | `labels` | Labels / éditeurs |
| `CREATE_TABLE_COMPANIES.sql` | `companies` | Sociétés impliquées |
| `CREATE_TABLE_IMAGES.sql` | `images` | Pochettes et images |
| `CREATE_TABLE_VIDEOS.sql` | `videos` | Vidéos liées sur Discogs |
| `CREATE_TABLE_IDENTIFIERS.sql` | `identifiers` | Identifiants (barcode, etc.) |
| `CREATE_TABLE_SERIES.sql` | `series` | Séries de releases |
| `CREATE_TABLE_EXTRAARTISTS.sql` | `extraartists` | Artistes additionnels |
| `CREATE_TABLE_SUBMITTER.sql` | `submitter` | Soumetteur de la release |
| `CREATE_TABLE_CONTRIBUTORS.sql` | `contributors` | Contributeurs |

**Utilitaires Python** (`py_utils/`) :
- `extract_tables.py` : extrait les `CREATE TABLE` depuis le schéma SQLite et les écrit en fichiers `.sql`
- `get_schema.py` : affiche la structure complète de la base (tables, colonnes, clés)

### `sql/CREATE_VIEWS/`

| Script | Vue | Description |
|---|---|---|
| `CREATE_VIEW_MUSICDISG.sql` | `musicdisg` | Vue consolidée joignant `music`, `discogs`, `discogs_main` et `rating` — utilisée par l'interface web Music & Discogs |

### `sql/ETL_SCRIPTS/`

| Script | Description |
|---|---|
| `CONSOLIDATE.sql` | Requête de jointure `music × discogs × discogs_main × rating` (même logique que la vue `musicdisg`) |
| `EASY_EXECUTE.py` | Exécute `CONSOLIDATE.sql` et exporte le résultat en CSV (`output.csv`) |
| `GET_STRUCT.sql` | Requête d'introspection du schéma SQLite (tables + colonnes) |

---

## Schéma de base de données (MPD)

```mermaid
erDiagram
    music {
        TEXT etag PK
        TEXT id
        TEXT videoId
        TEXT Discogged
        TEXT playlistId
        TEXT channelId
        TEXT title
    }

    discogs {
        TEXT id PK
        TEXT master_id
        TEXT Z_tech_index
        TEXT etag
        TEXT title
        TEXT country
        TEXT year
    }

    discogs_main {
        TEXT id_main PK
        TEXT id
        TEXT title
        TEXT status
        TEXT master_id
        TEXT year
        TEXT country
        TEXT released
    }

    community {
        TEXT id_main FK
        TEXT have
        TEXT want
        TEXT data_quality
        TEXT status
    }

    rating {
        TEXT id_main FK
        TEXT count
        TEXT average
    }

    submitter {
        TEXT id_main FK
        TEXT username
        TEXT resource_url
    }

    contributors {
        TEXT id_main FK
        TEXT username
        TEXT resource_url
    }

    artists {
        TEXT id_main FK
        TEXT id
        TEXT name
        TEXT role
        TEXT tracks
    }

    extraartists {
        TEXT id_main FK
        TEXT id
        TEXT name
        TEXT role
    }

    labels {
        TEXT id_main FK
        TEXT id
        TEXT name
        TEXT catno
    }

    companies {
        TEXT id_main FK
        TEXT id
        TEXT name
        TEXT catno
        TEXT entity_type
    }

    series {
        TEXT id_main FK
        TEXT id
        TEXT name
        TEXT catno
    }

    formats {
        TEXT id_main FK
        TEXT name
        TEXT qty
        TEXT descriptions
    }

    identifiers {
        TEXT id_main FK
        TEXT type
        TEXT value
    }

    images {
        TEXT id_main FK
        TEXT type
        TEXT uri
        TEXT width
        TEXT height
    }

    tracklist {
        TEXT id_main FK
        TEXT position
        TEXT title
        TEXT duration
        TEXT artists
    }

    videos {
        TEXT id_main FK
        TEXT uri
        TEXT title
        TEXT duration
    }

    music ||--o{ discogs : "etag"
    discogs ||--o| discogs_main : "id -> id_main"
    discogs_main ||--|| community : "id_main"
    discogs_main ||--|| rating : "id_main"
    discogs_main ||--o| submitter : "id_main"
    discogs_main ||--o{ contributors : "id_main"
    discogs_main ||--o{ artists : "id_main"
    discogs_main ||--o{ extraartists : "id_main"
    discogs_main ||--o{ labels : "id_main"
    discogs_main ||--o{ companies : "id_main"
    discogs_main ||--o{ series : "id_main"
    discogs_main ||--o{ formats : "id_main"
    discogs_main ||--o{ identifiers : "id_main"
    discogs_main ||--o{ images : "id_main"
    discogs_main ||--o{ tracklist : "id_main"
    discogs_main ||--o{ videos : "id_main"
```

### Relations clés

| Source | Destination | Jointure |
|---|---|---|
| `music` | `discogs` | `music.etag = discogs.etag` |
| `discogs` | `discogs_main` | `discogs.id = discogs_main.id_main` |
| `discogs_main` | toutes les sous-tables | `discogs_main.id_main = *.id_main` |