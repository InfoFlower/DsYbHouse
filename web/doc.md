# web/ — Documentation technique

> Interface web de HOUSIFY : pages HTML/CSS/JS vanilla communiquant avec le backend Flask via API REST.

---

## Vue d'ensemble

Chaque sous-dossier correspond à une page de l'application. Les fichiers statiques sont servis par Flask via la route `/web/<path>`.

| Page | Dossier | Description |
|---|---|---|
| Accueil | `index/` | Navigation principale vers les autres pages |
| Récupération de vidéos | `retreive_videos/` | Formulaire d'import YouTube (chaîne ou playlist) |
| Vidéos sauvegardées | `view_videos/` | Consultation de la table `music` avec filtres |
| Music & Discogs | `view_musicdisg/` | Vue consolidée YouTube + Discogs avec filtres avancés |

Le fichier `logo.svg` à la racine de `web/` est partagé par toutes les pages.

---

## Pages

### `index/`

Page d'accueil minimaliste avec trois boutons de navigation :
- Retrieve Videos → `retreive_videos/page.html`
- View Saved Videos → `view_videos/page.html`
- Music Discogs → `view_musicdisg/page.html`

**Fichiers** : `page.html`, `script.js` (vide), `styles.css`

### `retreive_videos/`

Formulaire permettant de récupérer des vidéos YouTube :
- Sélection du type : **Channel** (username) ou **Playlist** (ID)
- Champ de recherche
- Case à cocher « Enregistrer dans la BDD »
- Affichage des résultats en grille avec liens YouTube

**API appelée** : `GET /api/get_videos/<search>/<type>/<need_db>`

**Fichiers** : `page.html`, `script.js`, `styles.css`

### `view_videos/`

Consultation de la vidéothèque locale (table `music`) :
- Filtres dynamiques par **titre** et **chaîne** (multi-sélection, cascading)
- Toggle **grille / liste**
- Bouton de réinitialisation des filtres

**API appelée** : `GET /api/see_database/`

**Fichiers** : `page.html`, `script.js`, `styles.css`

### `view_musicdisg/`

Page la plus riche — affiche les données consolidées YouTube + Discogs :
- Filtres multi-critères : **chaîne**, **genre**, **année**, **rating** Discogs
- Tri par titre, année, rating, prix
- Toggle **grille / liste**
- Affichage des métadonnées Discogs : genre, style, pays, année, prix, note communautaire

**API appelée** : `GET /api/consolidated_data/send_musicdiscg/`

**Fichiers** : `page.html`, `script.js`, `styles.css`

---

## Navigation

Toutes les pages partagent un menu de navigation horizontal (`<nav class="top-menu">`) avec quatre liens :
- Home → `index/page.html`
- Retrieve Videos → `retreive_videos/page.html`
- Saved Videos → `view_videos/page.html`
- Music Discogs → `view_musicdisg/page.html`

---

## Interactions avec le backend

| Page | Endpoint Flask | Données retournées |
|---|---|---|
| `retreive_videos` | `/api/get_videos/<search>/<type>/<need_db>` | `{status, videos, header, count}` |
| `view_videos` | `/api/see_database/` | `{status, header, videos}` |
| `view_musicdisg` | `/api/consolidated_data/send_musicdiscg/` | `{status, header, videos, count}` |
