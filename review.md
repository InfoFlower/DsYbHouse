# HOUSIFY — Revue de code

> Analyse de la structure, des redondances et des bugs identifiés dans le code.
> Dernière revue : avril 2026

---

## TODO — Améliorations à appliquer

### Bugs à corriger (priorité haute)

- [ ] **`consolidate_discoggs_data()` : clé API Discogs en dur** — `api_key = "DEVELOPER_KEY"` au lieu d'utiliser la variable d'environnement (`Z_methods.py` L33)
- [ ] **`modifify_data()` : `first` jamais mis à `False` en mode column** — le `first = False` est dans le bloc `type_of_struct == 'row'` uniquement, ce qui fait que la condition ` OR ` ne s'applique jamais correctement en mode column (`DB_Manager.py` L133-140)
- [ ] **`import_discord_database()` : `break` au lieu de `continue`** — une erreur sur un seul ID arrête tout le pipeline au lieu de passer au suivant (`Z_methods.py` L66)
- [ ] **`get_all_data()` : mutation de `self.base_url` non thread-safe** — si deux appels concurrents, le `base_url` sera corrompu (`API_Discogs.py` L33-43)
- [ ] **`create_table()` dans `db_manager` : chemin vers `data/sql/CREATE/`** — le chemin référence `CREATE/` mais les fichiers sont dans `CREATE_TABLES/` (`DB_Manager.py` L96)
- [ ] **`receive_json()` : `delete_field` non défini si `type` invalide** — si `type` n'est ni `PLAYLIST` ni `USER`, `delete_field` n'existe pas et l'écriture en base crash (`flask_server.py` L30-37)
- [ ] **`insert_data()` : `except Exception` silencieux sur erreur de structure** — le bloc `except` capture toutes les exceptions (y compris `KeyError`, `TypeError`) et tente une correction aveugle au lieu de remonter l'erreur (`DB_Manager.py` L67-83)

### Redondances à éliminer (priorité moyenne)

- [ ] **`load_dotenv()` appelé 3 fois** — dans `DB_Manager.py`, `Z_methods.py` et `flask_server.py`. Centraliser dans un seul point d'entrée
- [ ] **Connexion SQLite ouverte/fermée à chaque opération** — `execute()`, `insert_data()`, `read_db()`, `modifify_data()` ouvrent et ferment chacun leur connexion. Utiliser un context manager ou une connexion réutilisable
- [ ] **`SingleLayerDataNormalizer` et `PlaylistDataNormalizer` : code quasi-identique** — même pattern (`flatten_data` dict de listes, `get_header_and_data()`, `get_number_of_videos()`, `__str__`). Extraire une classe de base `DataNormalizer`
- [ ] **`populateFilters()` et `resetFilters()` dupliqués** dans `view_videos/script.js` — le reset reconstruit manuellement les filtres au lieu de rappeler `populateFilters()`
- [ ] **Toggle grille/liste copié-collé** dans `view_videos/script.js` et `view_musicdisg/script.js` — même logique exacte, pourrait être un composant partagé
- [ ] **`DB_JsonHandler` duplique `db_manager`** — `DB_JsonHandler` encapsule `db_manager` mais recrée sa propre logique de `create_table()` avec du SQL brut, alors que `db_manager.create_table()` existe déjà

### Améliorations structurelles (priorité basse)

- [ ] **Ajouter un `requirements.txt`** — les dépendances sont listées dans le readme mais pas dans un fichier standard
- [ ] **Renommer `modifify_data`** → `modify_data` (typo)
- [ ] **Renommer `JSON_Discord_SingleLayer.py`** → le fichier gère des données Discogs, pas Discord
- [ ] **Renommer `retreive_videos/`** → `retrieve_videos/` (typo)
- [ ] **Supprimer les `print()` de debug** dans `DB_Manager.py` (L41, L65, L90, L117, L134) et `DB_JsonHandler.py` (L18)
- [ ] **Supprimer `import numpy`, `import pandas`, `from polars import first`** dans `DB_Manager.py` — `numpy` n'est jamais utilisé, `pandas` sert uniquement pour un export CSV de debug, `polars.first` est importé mais jamais utilisé
- [ ] **Supprimer `consolidate_discoggs_data` de l'import Flask** — importé dans `flask_server.py` L4 mais jamais utilisé (la route a été supprimée)
- [ ] **Ajouter un `.gitignore`** pour exclure `housify.db`, `log.txt`, `*.csv` de debug, `.env`

---

## Analyse détaillée

### 1. Structure du code

#### Points positifs
- **Séparation claire des responsabilités** : APIs (`API_*.py`), base de données (`DB_*.py`), normalisation (`JSON_*.py`), orchestration (`Z_methods.py`)
- **Héritage API cohérent** : `BaseAPI` → `Mid_level_API` → `High_level_API` est un bon pattern
- **Schéma évolutif** : `_ensure_columns()` est une bonne idée pour un projet en phase de prototypage
- **Frontend simple et fonctionnel** : les pages font le travail sans framework lourd

#### Points à améliorer

**Pas de gestion centralisée de la configuration**

`load_dotenv()` et `os.getenv('WD')` sont appelés indépendamment dans chaque fichier. Un module `config.py` unique éviterait les incohérences et la répétition.

```python
# Proposition : src/config.py
import os
from dotenv import load_dotenv
load_dotenv()

WD = os.getenv('WD')
YTB_API = os.getenv('YTB_API')
DB_PATH = f"{WD}/data/housify.db"
```

**Pas de gestion des connexions SQLite**

Chaque méthode de `db_manager` ouvre et ferme sa propre connexion. Cela fonctionne mais est inefficace et empêche les transactions multi-opérations. `write_db` appelle `modifify_data` (connexion 1) puis `insert_data` (connexion 2) — si l'insert échoue après le delete, les données sont perdues.

```python
# Proposition : utiliser un context manager
class db_manager:
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self
    def __exit__(self, *args):
        self.conn.close()
```

**Nommage incohérent**

| Actuel | Problème |
|---|---|
| `modifify_data` | Typo (`modifify` → `modify`) |
| `JSON_Discord_SingleLayer.py` | C'est Discogs, pas Discord |
| `retreive_videos/` | Typo (`retreive` → `retrieve`) |
| `import_discord_database()` | C'est Discogs, pas Discord |
| `consolidate_discoggs_data()` | Double G dans `discoggs` |
| `Z_methods.py` | Le préfixe `Z_` ne porte pas de sens |

**`sys.path.append('src')` dans `Z_methods.py`**

Ce hack de path rend les imports fragiles. Quand `Z_methods.py` est importé depuis `flask_server.py` (qui utilise `from src.Z_methods import ...`), le `sys.path.append('src')` ajoute un chemin relatif qui dépend du répertoire de travail. Préférer des imports relatifs ou un `__init__.py`.

---

### 2. Fonctionnalités redondantes

#### Deux systèmes de création de tables

- `db_manager.create_table()` lit un fichier `.sql` depuis `data/sql/CREATE/`
- `DB_JsonHandler.create_table()` génère du `CREATE TABLE IF NOT EXISTS` dynamiquement à partir des clés du dictionnaire JSON

Les deux coexistent sans interaction. Le second rend le premier obsolète pour les tables Discogs, mais le premier reste nécessaire pour la table `music`. Il faudrait choisir un seul mécanisme.

#### Deux normalizers mono-niveau quasi-identiques

`SingleLayerDataNormalizer` et `PlaylistDataNormalizer` partagent :
- Un dictionnaire de listes comme stockage interne
- `get_header_and_data()` → `(header, list[tuple])`
- `get_number_of_videos()` → `int`
- `__str__()` → format CSV

La seule différence : `PlaylistDataNormalizer` a des colonnes prédéfinies et extrait des champs imbriqués spécifiques à YouTube, tandis que `SingleLayerDataNormalizer` est générique. Une classe de base extrairait ~60% du code dupliqué.

#### Export CSV en double

- `EASY_EXECUTE.py` exécute `CONSOLIDATE.sql` et écrit `output.csv`
- `test.py` exécute la même donnée (table `musicdisg`) et écrit `musicdisg.json`
- `insert_data()` écrit `modified_data.csv` en cas d'erreur de structure

Trois exports de debug différents, aucun n'est nettoyé.

---

### 3. Bugs et risques identifiés

#### BUG CRITIQUE : Clé API Discogs en dur

```python
# Z_methods.py L33
def consolidate_discoggs_data(max_results=None, overwrite_db=False):
    ...
    api_key = "DEVELOPER_KEY"  # ← clé en dur, jamais fonctionnelle
    api = Mid_level_API(api_key)
```

La variable locale `api_key` masque la variable globale du même nom (L11). La fonction utilisera toujours `"DEVELOPER_KEY"` comme clé, ce qui fera échouer toutes les requêtes à l'API Discogs search (qui nécessite une authentification).

#### BUG : `break` au lieu de `continue` dans `import_discord_database()`

```python
# Z_methods.py L63-67
except Exception as e:
    time.sleep(1)
    print(f"Error fetching data for id {i[0]}: {e}")
    break  # ← arrête tout le pipeline au lieu de passer au suivant
```

Une seule erreur réseau ou API interrompt l'enrichissement complet. Devrait être `continue` avec logging de l'ID en échec.

#### BUG : Mutation de `base_url` non thread-safe

```python
# API_Discogs.py L33-43
def get_all_data(self, release_id, no_key=True):
    memory_base_url = self.base_url
    self.base_url = "https://api.discogs.com/releases"  # ← mutation d'état
    try:
        result = self._request(release_id, {}, no_key=no_key)
        self.base_url = memory_base_url  # ← restauration
        return result
    except:
        self.base_url = memory_base_url
        return None
```

Le pattern save/restore de `self.base_url` est fragile. Si Flask traite deux requêtes en parallèle (ou si l'ordonnanceur AUTOMATE est activé), l'état sera corrompu. Solution : passer l'URL en paramètre à `_request()` au lieu de muter l'instance.

#### RISQUE : Injection SQL via `table_name`

```python
# DB_Manager.py — plusieurs endroits
c.execute(f"SELECT * FROM {table_name}")
c.execute(f"DELETE FROM {table_name} WHERE {condition}")
c.execute(f"PRAGMA table_info({table_name})")
```

Les noms de tables sont injectés directement dans les requêtes SQL via f-string. Actuellement les valeurs viennent du code interne, mais si une route Flask finit par accepter un nom de table en paramètre, c'est une injection SQL. Préférer une whitelist de tables autorisées.

#### RISQUE : `except Exception` trop large dans `insert_data()`

```python
# DB_Manager.py L66-83
try:
    if type_of_struct == 'column' and isinstance(data[0], (list, tuple)):
        data = [[data[i][r] for i in range(len(header_list))] for r in range(len(data[0]))]
except Exception as e:
    # ← capture TOUT : IndexError, TypeError, KeyError...
    # tente une correction aveugle des longueurs
```

Ce bloc masque les vrais bugs. Un `TypeError` dû à un mauvais type de données sera traité comme un problème de longueur de colonnes. Restreindre au minimum à `except (IndexError, ValueError)`.

---

### 4. Frontend

#### Points positifs
- `escapeHtml()` dans `view_musicdisg/script.js` — bonne protection contre le XSS
- Filtres cascading dans `view_videos` — UX correcte

#### Points à améliorer

- **Pas d'`escapeHtml()` dans `retreive_videos/script.js`** — `videoObj.title` et `videoObj.description` sont injectés directement dans le HTML via template string. Risque XSS si un titre YouTube contient du HTML
- **Le `displayVideos()` dans `retreive_videos/script.js` et `view_videos/script.js` est copié-collé** avec des variations mineures
- **Pas de gestion d'erreur côté serveur** — les routes Flask ne renvoient jamais de code HTTP d'erreur (toujours 200), même en cas d'échec. Le frontend ne peut pas distinguer un vrai succès d'un échec silencieux
