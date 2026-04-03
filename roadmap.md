# HOUSIFY — Roadmap

> Application locale de gestion d'une vidéothèque musicale, croisant des données YouTube et Discogs.

---

## ✅ Réalisations terminées

### Infrastructure & Backend
- [x] **Serveur Flask** — point d'entrée unique (`flask_server.py`), configuration via `.env` (`WD`, `YTB_API`)
- [x] **Couche API générique** (`API_Base.py`) — `BaseAPI` paramétrable (base URL + clé), gestion des requêtes HTTP
- [x] **Intégration YouTube Data API v3** (`API_Youtube.py`) — récupération par chaîne (`USER`) ou par playlist (`PLAYLIST`), pagination automatique, filtrage des vidéos privées/supprimées
- [x] **Intégration Discogs API** (`API_Discogs.py`) — recherche de releases par titre, retry exponentiel en cas d'erreur
- [x] **Base de données SQLite** (`data/housify.db`) — deux tables `music` et `discogs` avec schémas versionés dans `data/sql/CREATE/`
- [x] **DB Manager** (`DB_Manager.py`) — CRUD complet : création de table à la volée, insert, delete conditionnel, update, read avec requête libre
- [x] **Normalisation des données YouTube** (`JSON_Youtube_Playlist.py`) — aplatissement de la réponse paginée → tuples insérables en base
- [x] **Normalisation des données Discogs** (`JSON_Global_SingleLayer.py`) — normalisation générique de listes JSON mono-niveau
- [x] **Déduplication à l'ingestion** — suppression des anciens enregistrements sur un champ clé avant ré-insertion (`delete_on`)
- [x] **Scripts ETL SQL** — `CONSOLIDATE.sql` (jointure music × discogs), `EASY_EXECUTE.py` (exécution et export formaté en ASCII)

### Frontend
- [x] **Page d'accueil** (`web/index/`) — navigation principale
- [x] **Page de récupération de vidéos** (`web/retreive_videos/`) — formulaire sélection type (chaîne / playlist), option sauvegarde en base, affichage des résultats en grille
- [x] **Page de visualisation** (`web/view_videos/`) — lecture de la base `music`, toggle vue grille / liste
- [x] **Routing statique Flask** — tous les assets (HTML, CSS, JS) servis via `/web/<path>`

---

## 🔄 En cours

### Base décisionnelle de consolidation Music × Discogs
- Script SQL `CONSOLIDATE.sql` existant (jointure `title` entre les deux tables), mais la liaison n'est pas encore formalisée en clé étrangère ni exposée en API
- Le champ `Discogged` dans la table `music` indique si un titre a été enrichi (`'Y'`) — logique de marquage implémentée dans `Z_methods.py`
- L'enrichissement se fait titre par titre avec un délai de 1 s (rate limiting manuel) ; pas encore de reprise sur erreur ni de bilan d'exécution
- Route `/api_dev/consolidate_discogs_data/send_current_db/` expose la table `discogs` brute, mais aucune vue consolidée n'est encore exposée

### Ordonnanceur de tâches (`AUTOMATE/`)
- Classe `task` fonctionnelle : threading, suivi statut (`PENDING / RUNNING / COMPLETED / ERROR`), mesure CPU & mémoire via `psutil`
- Classe `scheduler` initialisée (file ordonnée, gestion de dépendances, concurrence max configurable) — méthode `run()` non implémentée
- `AUTO_Head.py` référence un `RequestHandler` dans `AUTOMATE/TASKS` qui n'existe pas encore
- Les fichiers `routes.csv` et `schedule.csv` sont présents mais non exploités

---

## 🗓️ Réalisations futures

### Données & enrichissement
- [ ] **Liaison formelle Music × Discogs** — créer une table de jointure ou une vue SQL `music_enriched` exposant les métadonnées Discogs consolidées (genre, style, année, pays) sur chaque vidéo
- [ ] **Alimentation automatique de la wishlist Discogs** — détecter les titres présents dans `music` mais absents de la collection Discogs et les pousser automatiquement via l'API Discogs Write
- [ ] **Enrichissement complet de la base** — lancer l'ordonnanceur pour enrichir tous les titres en arrière-plan, avec bilan (nb enrichis / échecs / déjà traités)

### Lecture & expérience utilisateur
- [ ] **Lecture des musiques via le site** — intégrer un lecteur YouTube embarqué (iframe ou `youtube-iframe-api`) directement dans les pages `view_videos` et `view_videos` pour écouter sans quitter l'application
- [ ] **Page de notation des musiques** — interface permettant d'attribuer une note (étoiles ou score) à chaque vidéo enregistrée en base, avec persistance dans la table `music`
- [ ] **Filtres & recherche dans la vidéothèque** — filtrer par genre Discogs, chaîne, année, note, statut d'enrichissement

### Utilisateurs & gestion
- [ ] **Système d'utilisateurs** — authentification légère (session Flask) pour permettre à plusieurs personnes de noter indépendamment
- [ ] **Historique des notations par utilisateur** — table `ratings` liée à `music` et aux users

### Automatisation
- [ ] **Finaliser l'ordonnanceur** — implémenter `scheduler.run()` : boucle de dispatch des tâches, gestion des dépendances, timeout, état persisté
- [ ] **`RequestHandler`** dans `AUTOMATE/TASKS` — gestionnaire de requêtes HTTP planifiables (rafraîchissement automatique des playlists, consolidation Discogs périodique)
- [ ] **Interface de gestion des tâches planifiées** — page web permettant de voir et déclencher les tâches de l'ordonnanceur

### Infrastructure
- [ ] **Containerisation Docker** — `Dockerfile` + `docker-compose` pour simplifier le déploiement sur le homelab
- [ ] **Tests automatisés** — couverture des modules `DB_Manager`, normalizers et API wrappers
