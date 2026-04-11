# HOUSIFY

Application homelab de gestion d'une collection musicale. Elle récupère les vidéos YouTube d'une chaîne ou d'une playlist, les stocke localement dans une base SQLite, et les enrichit avec les métadonnées Discogs (genre, année, pays, label, note communautaire, prix).

> Projet personnel, destiné à terme à être mis à disposition avec gestion de sessions utilisateur.

---

## Liens rapides

- [Documentation technique](doc.md) — architecture, flux de données, routes API
- [src/ — Code source](src/_doc.md) — APIs, BDD, normalisation JSON
- [data/ — Base de données](data/doc.md) — schéma SQLite, scripts SQL, MPD
- [web/ — Interface web](web/doc.md) — pages, filtres, interactions API
- [Roadmap](roadmap.md) — travaux en cours, prochaines étapes, historique

---

## Démarrage rapide

**Prérequis** : Python 3.11+, pip

```bash
# 1. Installer les dépendances
pip install flask python-dotenv requests tqdm pandas numpy psutil polars

# 2. Créer un fichier .env à la racine
#    WD=C:/chemin/absolu/vers/HOUSIFY
#    YTB_API=<votre clé API YouTube Data v3>

# 3. Lancer le serveur
python flask_server.py
# → http://localhost:5000
```

---

## Fonctionnalités

| Page | URL | Description |
|---|---|---|
| Accueil | `/` | Navigation principale |
| Récupérer des vidéos | `/web/retreive_videos/page.html` | Import de vidéos YouTube par chaîne ou playlist, avec option de sauvegarde en base |
| Vidéos sauvegardées | `/web/view_videos/page.html` | Consultation de la vidéothèque locale avec filtres par titre/chaîne, vue grille ou liste |
| Music & Discogs | `/web/view_musicdisg/page.html` | Vue consolidée YouTube + Discogs : filtres par genre, année, chaîne, rating ; tri par titre, année, note, prix |

### Enrichissement des données

En plus de l'interface web, HOUSIFY enrichit automatiquement les vidéos avec les données Discogs :

1. **Recherche Discogs** : chaque titre de la table `music` est recherché dans la base Discogs → résultats stockés dans `discogs`
2. **Import détaillé** : pour chaque release trouvée, les métadonnées complètes sont récupérées et découpées en tables relationnelles (`discogs_main`, `artists`, `tracklist`, `rating`, `formats`, `labels`…)
3. **Vue consolidée** : la vue SQL `musicdisg` joint toutes ces données pour l'affichage dans l'interface Music & Discogs

---

## Stack technique

| Couche | Technologie |
|---|---|
| Serveur | Python / Flask |
| Base de données | SQLite (`data/housify.db`) |
| APIs externes | YouTube Data API v3, Discogs API |
| Frontend | HTML / CSS / JS vanilla |
| Traitement données | pandas, numpy, tqdm |

---

## Structure du projet

```
flask_server.py              # Point d'entrée Flask
.env                         # Configuration (WD, YTB_API)
doc.md                       # Documentation technique racine
readme.md                    # Ce fichier
roadmap.md                   # Projection du projet
test.py                      # Script de test (export musicdisg en JSON)
│
├── src/                     # Code source Python
│   ├── API_Base.py          #   Client HTTP générique
│   ├── API_Youtube.py       #   API YouTube (Mid + High level)
│   ├── API_Discogs.py       #   API Discogs (recherche + détail)
│   ├── DB_Manager.py        #   CRUD SQLite
│   ├── DB_JsonHandler.py    #   Persistance JSON → tables dynamiques
│   ├── JSON_Basic.py        #   Utilitaires JSON
│   ├── JSON_Youtube_Playlist.py      # Normalisation YouTube
│   ├── JSON_Discord_SingleLayer.py   # Normalisation Discogs (recherche)
│   ├── JSON_Global_Multilayer.py     # Normalisation Discogs (détail multi-tables)
│   ├── Z_methods.py         #   Orchestration haut niveau
│   ├── AUTO_Head.py         #   Point d'entrée automate (stand-by)
│   └── AUTOMATE/            #   Système d'automatisation (stand-by)
│       ├── TASKS.py         #     Classe task (threading + monitoring)
│       ├── SCHEDULER.py     #     Ordonnanceur (non finalisé)
│       ├── routes.csv       #     Mapping tâches → routes
│       └── schedule.csv     #     Configuration planification
│
├── data/                    # Données
│   ├── housify.db           #   Base SQLite principale
│   ├── MUSIC.csv            #   Export de la table music
│   ├── raw_data.json        #   Données brutes d'import
│   ├── raw_info/            #   Cache JSON de releases Discogs
│   └── sql/                 #   Scripts SQL
│       ├── CREATE_TABLES/   #     CREATE TABLE pour chaque table
│       ├── CREATE_VIEWS/    #     Vue musicdisg (consolidation)
│       └── ETL_SCRIPTS/     #     Requêtes ETL + export CSV
│
├── web/                     # Interface web
│   ├── logo.svg             #   Logo partagé
│   ├── index/               #   Page d'accueil
│   ├── retreive_videos/     #   Import YouTube
│   ├── view_videos/         #   Vidéothèque locale
│   └── view_musicdisg/      #   Vue consolidée Music & Discogs
│
└── dump/                    # Exports bruts
    └── all_info.json        #   Dump complet d'une release Discogs
```

---

## API REST

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/get_videos/<search>/<type>/<need_db>` | Récupère les vidéos YouTube (`type`: `USER` ou `PLAYLIST`). Écrit en base si `need_db=true` |
| GET | `/api/see_database/` | Retourne le contenu de la table `music` |
| GET | `/api/consolidated_data/send_musicdiscg/` | Retourne la vue consolidée `musicdisg` |
