# HOUSIFY — Roadmap

> Application de gestion d'une collection musicale, croisant YouTube et Discogs.
> → [Documentation technique](doc.md) | [README](readme.md)

---

## 🔄 En cours

### [En stand-by] Automatisation de la mise à jour de la base de données

Le module `AUTOMATE/` est conçu pour automatiser la récolte et l'enrichissement des données. Le développement est **suspendu par choix de priorité** : les fonctionnalités utilisateur sont prioritaires avant la mise en place technique.

**État actuel :**
- Classe `task` (`TASKS.py`) : fonctionnelle — exécution threadée, suivi de statut (`PENDING`/`RUNNING`/`COMPLETED`/`ERROR`), mesure CPU/mémoire via `psutil`
- Classe `scheduler` (`SCHEDULER.py`) : structure en place (file ordonnée, dépendances, concurrence max) — méthode `run()` non implémentée
- `AUTO_Head.py` référence un `RequestHandler` qui n'existe pas encore
- Fichiers de configuration (`routes.csv`, `schedule.csv`) : vides

**Reste à faire :**
- Implémenter `scheduler.run()` (boucle de dispatch, gestion des dépendances, timeout)
- Créer `RequestHandler` pour le rafraîchissement planifié des playlists et consolidations
- Stabiliser `import_discord_database()` dans `Z_methods.py` (reprise sur erreur, logging des IDs en échec)

---

## 🗓️ Futur

### Système de notation interne

Permettre de noter les morceaux directement dans l'application (système d'étoiles) pour constituer une **liste de priorité d'achat**. La note interne sera distincte du rating communautaire Discogs déjà importé.

**Sous-tâches :**
- [ ] Nouvelle table `user_ratings` (lien `etag` → note)
- [ ] Endpoint API pour soumettre/modifier une note
- [ ] Composant d'étoiles dans `view_musicdisg` (clic pour noter)
- [ ] Tri et filtre par note interne
- [ ] Vue « liste de priorité » : morceaux triés par note décroissante

> Pour le passage en multi-utilisateur (sessions), une couche d'authentification devra être ajoutée en amont.

### Ajout à la wantlist Discogs

Intégrer l'API Discogs en écriture pour ajouter des releases à la **wishlist Discogs** directement depuis l'application.

**Sous-tâches :**
- [ ] Authentification OAuth Discogs (nécessite un token utilisateur)
- [ ] Bouton « Ajouter à ma wantlist » sur chaque release dans `view_musicdisg`
- [ ] Endpoint API Flask → appel `PUT /users/{username}/wants/{release_id}` sur l'API Discogs
- [ ] Feedback visuel (ajouté / déjà dans la wantlist / erreur)

### Intégration Spotify

Reproduire le fonctionnement actuel de YouTube avec Spotify : **importer des playlists et des morceaux d'artistes** depuis Spotify.

**Sous-tâches :**
- [ ] Enregistrement d'une application Spotify Developer (Client ID / Secret)
- [ ] Authentification OAuth 2.0 (Authorization Code Flow)
- [ ] Nouveau module `API_Spotify.py` (héritant de `BaseAPI`)
- [ ] Import de playlists Spotify → table `music` (ou nouvelle table `music_spotify`)
- [ ] Import des morceaux d'un artiste Spotify
- [ ] Croisement Spotify ↔ Discogs (par titre + artiste)

**Limites connues :**
- L'API Spotify nécessite une authentification OAuth2 utilisateur (pas de simple clé API comme YouTube)
- Les quotas Spotify sont plus restrictifs pour les applications non vérifiées
- Le matching automatique Spotify ↔ Discogs sera approximatif (titres non identiques, versions multiples)
- La lecture audio via Spotify nécessite un compte Premium et le Spotify Web Playback SDK

### Suggestions complémentaires

Basé sur l'architecture actuelle et la direction du projet, voici d'autres évolutions logiques :

- [ ] **Lecteur embarqué** : intégrer le YouTube IFrame Player API dans `view_musicdisg` pour écouter les morceaux sans quitter l'app — essentiel pour pouvoir noter en écoutant
- [ ] **Sessions utilisateur** : authentification légère (session Flask ou JWT) pour permettre la notation multi-utilisateur et préparer la mise à disposition
- [ ] **Dockerisation** : `Dockerfile` + `docker-compose` pour un déploiement homelab simplifié — prérequis pour la mise à disposition
- [ ] **Scalabilité BDD** : migration SQLite → PostgreSQL si le volume de données ou le nombre d'utilisateurs croît
- [ ] **Tests automatisés** : couverture des modules critiques (`DB_Manager`, normalizers, wrappers API) pour fiabiliser avant mise à disposition
- [ ] **Page dashboard** : vue synthétique de la collection (nombre de morceaux, répartition par genre/année/chaîne, stats d'enrichissement)

---

## ✅ Passé

### Avril 2026 — Import Discogs multi-tables & vue consolidée

- **`JSON_Global_Multilayer`** : normalisation récursive du JSON complet d'une release Discogs en graphe de tables relationnelles (`discogs_main`, `artists`, `tracklist`, `rating`, `formats`, `labels`, `companies`, `images`, `videos`…)
- **`DB_JsonHandler`** : persistance dynamique du graphe de tables (création + insertion en mode colonne)
- **`API_Discogs.get_all_data(release_id)`** : appel vers l'endpoint public `/releases/<id>`
- **`Z_methods.import_discord_database()`** : pipeline d'import complet (lecture `discogs` → fetch détaillé → normalisation → insertion multi-tables)
- **17 scripts `CREATE TABLE`** générés automatiquement via `extract_tables.py`
- **Vue SQL `musicdisg`** : jointure `music ⟕ discogs ⟕ discogs_main ⟕ rating`
- **Page `view_musicdisg`** : interface web complète avec filtres multi-critères (genre, année, chaîne, rating), tri par titre/année/note/prix, toggle grille/liste
- **Route `/api/consolidated_data/send_musicdiscg/`** : exposition de la vue consolidée

### Avril 2026 — Enrichissement Discogs & base de données

- **`consolidate_discoggs_data()`** : enrichissement des titres `music` via la recherche Discogs avec marqueur `Discogged='Y'`
- **`SingleLayerDataNormalizer`** : normalisation des résultats de recherche Discogs avec injection de clé étrangère (`etag`)
- **Schéma évolutif** : `_ensure_columns()` ajoute dynamiquement les colonnes manquantes via `ALTER TABLE`
- **Support `type_of_struct`** : gestion des structures en colonnes et en lignes dans `write_db` / `insert_data` / `modifify_data`
- **Scripts ETL** : `CONSOLIDATE.sql` + `EASY_EXECUTE.py` pour l'export CSV
- **Barre de progression** : `tqdm` intégré dans les boucles d'enrichissement

### Avril 2026 — Import YouTube & fondations

- **Serveur Flask** : point d'entrée unique, configuration `.env`
- **API YouTube** : `High_level_API.get_all_videos()` — récupération par chaîne ou playlist, pagination, filtrage des vidéos privées/supprimées
- **`DB_Manager`** : CRUD SQLite complet (create, write, read, delete, update)
- **`PlaylistDataNormalizer`** : aplatissement des réponses YouTube paginées
- **Base SQLite** : tables `music` et `discogs`
- **Frontend** : page d'accueil, formulaire de récupération YouTube, page de visualisation avec filtres et toggle grille/liste
- **Module `AUTOMATE/`** : classes `task` et `scheduler` (pose des fondations)

### Mars 2026 — Commit initial

- Structure du projet, import du CSV initial, première base SQLite, premier serveur Flask, premières pages web
