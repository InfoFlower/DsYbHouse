# HOUSIFY — Roadmap

> Application locale de gestion d'une vidéothèque musicale, croisant des données YouTube et Discogs.
> → [Documentation technique](doc.md)

---

## ✅ Réalisations terminées

### Infrastructure & Backend
- [x] **Serveur Flask** — point d'entrée unique (`flask_server.py`), configuration via `.env` (`WD`, `YTB_API`)
- [x] **Couche API générique** (`API_Base.py`) — `BaseAPI` paramétrable (base URL + clé) ; option `no_key` pour les endpoints publics
- [x] **Intégration YouTube Data API v3** (`API_Youtube.py`) — récupération par chaîne (`USER`) ou par playlist (`PLAYLIST`), pagination automatique, filtrage des vidéos privées/supprimées
- [x] **Intégration Discogs API — recherche** (`API_Discogs.py`) — recherche de releases par titre, retry exponentiel en cas d'erreur
- [x] **Base de données SQLite** (`data/housify.db`) — tables `music` et `discogs` avec schémas versionnés dans `data/sql/CREATE/`
- [x] **DB Manager** (`DB_Manager.py`) — CRUD complet : création de table à la volée, insert, delete conditionnel, update, read avec requête libre
- [x] **Schéma évolutif sans migration** — `_ensure_columns()` ajoute automatiquement les colonnes manquantes via `ALTER TABLE`
- [x] **Support structures colonne / ligne** — `type_of_struct` dans `write_db` / `insert_data` / `modifify_data` pour gérer les deux orientations de données
- [x] **Normalisation des données YouTube** (`JSON_Youtube_Playlist.py`) — aplatissement de la réponse paginée → tuples insérables en base
- [x] **Normalisation des données Discogs mono-niveau** (`JSON_Discord_SingleLayer.py`) — remplace `JSON_Global_SingleLayer.py` ; supporte l'injection d'une clé étrangère (`added_key` / `added_value`) pour lier les releases Discogs à la table `music` via `etag`
- [x] **Déduplication à l'ingestion** — suppression des anciens enregistrements sur un champ clé avant ré-insertion (`delete_on`)
- [x] **Suivi de l'enrichissement** — champ `Discogged` dans `music` marqué `'Y'` après consolidation ; reprise possible sur les titres non traités
- [x] **Barre de progression** — `tqdm` intégré dans les boucles d'enrichissement (`consolidate_discoggs_data`, `import_discord_database`)
- [x] **Scripts ETL SQL** — `CONSOLIDATE.sql` (jointure music × discogs), `EASY_EXECUTE.py` (exécution et export formaté ASCII)

### Frontend
- [x] **Page d'accueil** (`web/index/`) — navigation principale
- [x] **Page de récupération de vidéos** (`web/retreive_videos/`) — formulaire sélection type (chaîne / playlist), option sauvegarde en base, affichage des résultats en grille
- [x] **Page de visualisation** (`web/view_videos/`) — lecture de la base `music`, toggle vue grille / liste
- [x] **Routing statique Flask** — tous les assets (HTML, CSS, JS) servis via `/web/<path>`

---

## 🔄 En cours

### Base décisionnelle Discogs multi-niveaux
- **`JSON_Global_Multilayer`** (nouveau) : parcourt récursivement le JSON complet d'une release Discogs (`/releases/<id>`) et le décompose en un graphe de tables relationnelles (`discogs_main`, + tables enfants pour tracklist, formats, labels…)
- **`DB_JsonHandler`** (nouveau) : persist ce graphe de tables — crée dynamiquement les tables et insère en mode colonne
- **`API_Discogs.get_all_data(release_id)`** (nouveau) : appel sans clé vers l'endpoint public `/releases/<id>`
- **`Z_methods.import_discord_database()`** (nouveau) : orchestre le pipeline complet — lit les ids de `discogs`, appelle `get_all_data`, normalise via `JSON_Global_Multilayer`, insère via `DB_JsonHandler` — **en cours de stabilisation** (gestion des erreurs partielles, reprise)
- La route Flask de consolidation Discogs (`/api_dev/consolidate_discogs_data/<max_results>/…`) est **temporairement commentée** le temps de migrer vers le nouveau pipeline

### Ordonnanceur de tâches (`AUTOMATE/`)
- Classe `task` fonctionnelle : threading, suivi statut (`PENDING / RUNNING / COMPLETED / ERROR`), mesure CPU & mémoire via `psutil`
- Classe `scheduler` : file ordonnée avec dépendances et concurrence max configurable — méthode `run()` non encore implémentée
- `AUTO_Head.py` référence un `RequestHandler` dans `AUTOMATE/TASKS` qui n'existe pas encore
- `routes.csv` et `schedule.csv` présents mais non exploités

---

## 🗓️ Réalisations futures

### Données & enrichissement
- [ ] **Stabiliser `import_discord_database`** — reprise sur erreur, logging des ids en échec, bilan d'exécution
- [ ] **Réexposer la consolidation Discogs en API** — rétablir la route Flask une fois le nouveau pipeline stable
- [ ] **Vue consolidée Music × Discogs** — vue SQL ou table `music_enriched` exposant genre, style, année, pays sur chaque vidéo
- [ ] **Alimentation automatique de la wishlist Discogs** — détecter les titres dans `music` absents de la collection et les pousser via l'API Discogs Write
- [ ] **Enrichissement complet en tâche de fond** — déclencher via l'ordonnanceur avec bilan (enrichis / échecs / déjà traités)

### Lecture & expérience utilisateur
- [ ] **Lecture des musiques via le site** — lecteur YouTube embarqué (`youtube-iframe-api`) dans `view_videos`
- [ ] **Page de notation des musiques** — note (étoiles / score) par vidéo, persistée en base
- [ ] **Filtres & recherche dans la vidéothèque** — par genre Discogs, chaîne, année, note, statut d'enrichissement

### Utilisateurs & gestion
- [ ] **Système d'utilisateurs** — authentification légère (session Flask) pour notation multi-utilisateurs
- [ ] **Historique des notations** — table `ratings` liée à `music` et aux users

### Automatisation
- [ ] **Finaliser `scheduler.run()`** — boucle de dispatch, gestion des dépendances, timeout, état persisté
- [ ] **`RequestHandler`** dans `AUTOMATE/TASKS` — rafraîchissement planifié des playlists et consolidations périodiques
- [ ] **Interface web de l'ordonnanceur** — page de suivi et déclenchement des tâches

### Infrastructure
- [ ] **Containerisation Docker** — `Dockerfile` + `docker-compose` pour le homelab
- [ ] **Tests automatisés** — couverture de `DB_Manager`, des normalizers, des wrappers API
