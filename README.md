# Rob - API ETL avec Robyn et MongoDB

Une API ETL (Extract, Transform, Load) moderne et performante construite avec [Robyn](https://github.com/sparckles/robyn) et MongoDB. Ce projet démontre comment créer un pipeline de données asynchrone pour extraire des données d'une API externe, les transformer et les stocker dans MongoDB.

## 🚀 Fonctionnalités

- **Pipeline ETL asynchrone** : Extraction, transformation et chargement de données
- **API REST rapide** : Propulsée par Robyn, un framework web Python ultra-rapide
- **Stockage MongoDB** : Persistance des données avec support MongoDB Atlas
- **Validation Pydantic** : Validation robuste des données à chaque étape du pipeline
- **Logging professionnel** : Traçabilité complète avec timestamps et niveaux de log
- **Type hints complets** : Code type-safe avec annotations Python modernes
- **Architecture modulaire** : Séparation claire entre modèles, pipeline et API
- **Gestion d'environnement** : Configuration via variables d'environnement
- **Gestion d'erreurs** : Traitement robuste des erreurs avec logs détaillés

## 📋 Prérequis

- Python >= 3.14
- MongoDB (local ou MongoDB Atlas)
- uv (gestionnaire de paquets Python) ou pip

## 🛠️ Installation

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd rob
```

### 2. Installer les dépendances

Avec uv (recommandé) :
```bash
uv sync
```

Ou avec pip :
```bash
pip install -e .
```

### 3. Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DB_NAME=votre_base_de_donnees
COLLECTION_NAME=users
```

**Note** : Remplacez les valeurs par vos propres identifiants MongoDB.

## 🎯 Utilisation

### Démarrer le serveur

```bash
python main.py
```

Le serveur démarre sur `http://localhost:8080`

### Endpoints disponibles

#### 1. Page d'accueil
```bash
GET /
```
Retourne un message de bienvenue.

**Réponse** :
```
Bienvenue sur l'API ETL ! Fais un POST sur /run-pipeline pour lancer.
```

#### 2. Lancer le pipeline ETL
```bash
POST /run-pipeline
```

Déclenche le pipeline complet :
- **Extract** : Récupère les utilisateurs depuis l'API JSONPlaceholder
- **Transform** : Formate et nettoie les données
- **Load** : Insère les données dans MongoDB

**Réponse** :
```json
{
  "status": "success",
  "inserted_count": 10,
  "message": "10 utilisateurs traités avec succès"
}
```

#### 3. Consulter les utilisateurs
```bash
GET /users
```

Récupère les 10 derniers utilisateurs stockés dans MongoDB.

**Réponse** :
```json
[
  {
    "external_id": 1,
    "full_name": "LEANNE GRAHAM",
    "email": "sincere@april.biz",
    "location": {
      "city": "Gwenborough",
      "geo": {
        "lat": "-37.3159",
        "lng": "81.1496"
      }
    },
    "company_name": "Romaguera-Crona",
    "pipeline_source": "Robyn-ETL"
  }
]
```

## 📁 Structure du projet

```
rob/
├── main.py              # Point d'entrée de l'API Robyn
├── pipeline.py          # Logique du pipeline ETL
├── models.py            # Modèles Pydantic pour validation
├── pyproject.toml       # Configuration du projet et dépendances
├── README.md            # Documentation
├── .env                 # Variables d'environnement (à créer)
└── .gitignore          # Fichiers à ignorer par Git
```

## 🔧 Architecture

### Modèles de données (`models.py`)

Le projet utilise **Pydantic** pour une validation robuste des données :

- **`RawUser`** : Modèle pour les données brutes de l'API JSONPlaceholder
  - Validation automatique des emails avec `EmailStr`
  - Sous-modèles : `Address`, `GeoLocation`, `Company`
  - Ignore les champs supplémentaires non définis

- **`TransformedUser`** : Modèle pour les données transformées
  - Validators personnalisés (nom en majuscules, email en minuscules)
  - Méthode `to_mongo_dict()` pour conversion MongoDB
  - Contraintes de validation (longueur minimale, format)

- **`PipelineResult`** : Modèle pour la réponse du pipeline
  - Status validé (success/error uniquement)
  - Compteur d'insertions (>= 0)
  - Message optionnel

### Pipeline ETL (`pipeline.py`)

La classe `UserPipeline` implémente le pattern ETL avec validation :

1. **Extract** : 
   - Appel asynchrone à l'API JSONPlaceholder avec `httpx`
   - Validation de chaque utilisateur avec Pydantic
   - Logs des utilisateurs invalides (ignorés)
   - Retourne `List[RawUser]`

2. **Transform** : 
   - Normalisation des noms (majuscules)
   - Normalisation des emails (minuscules)
   - Validation automatique via `TransformedUser`
   - Gestion d'erreur par utilisateur
   - Retourne `List[TransformedUser]`

3. **Load** : 
   - Conversion des modèles Pydantic en dictionnaires
   - Insertion en masse dans MongoDB avec `pymongo`
   - Gestion d'erreurs avec fermeture propre de la connexion

4. **Logging** :
   - Logs structurés avec timestamps
   - Niveaux appropriés (INFO, WARNING, ERROR)
   - Stack traces complètes pour les erreurs

### API REST (`main.py`)

- Framework : **Robyn** (async, haute performance)
- Logging de toutes les requêtes
- Routes :
  - `/` : Page d'accueil
  - `/run-pipeline` : Déclenchement du pipeline
  - `/users` : Consultation des données

## 📦 Dépendances

- **robyn** (>=0.76.0) : Framework web asynchrone
- **pymongo[srv]** (>=4.16.0) : Driver MongoDB
- **httpx** (>=0.28.1) : Client HTTP asynchrone
- **pydantic** (>=2.12.5) : Validation de données et sérialisation
- **python-dotenv** (>=1.2.1) : Gestion des variables d'environnement

## 🧪 Exemple d'utilisation

```bash
# 1. Démarrer le serveur
python main.py

# 2. Dans un autre terminal, lancer le pipeline
curl -X POST http://localhost:8080/run-pipeline

# 3. Consulter les données insérées
curl http://localhost:8080/users
```

## � Logging et Validation

### Exemple de logs du pipeline

Lorsque vous lancez le pipeline, vous verrez des logs détaillés :

```
2026-01-29 10:00:00 - __main__ - INFO - Démarrage de l'application Robyn sur le port 8080
2026-01-29 10:01:15 - __main__ - INFO - Requête POST reçue sur /run-pipeline - Démarrage du pipeline
2026-01-29 10:01:15 - pipeline - INFO - === Démarrage du pipeline ETL ===
2026-01-29 10:01:15 - pipeline - INFO - Début de l'extraction des données depuis l'API
2026-01-29 10:01:16 - pipeline - INFO - 10 utilisateurs récupérés depuis https://jsonplaceholder.typicode.com/users
2026-01-29 10:01:16 - pipeline - INFO - 10 utilisateurs validés sur 10
2026-01-29 10:01:16 - pipeline - INFO - Début de la transformation de 10 utilisateurs
2026-01-29 10:01:16 - pipeline - INFO - Transformation terminée: 10 utilisateurs traités
2026-01-29 10:01:16 - pipeline - INFO - Début du chargement des données dans MongoDB
2026-01-29 10:01:17 - pipeline - INFO - Succès: 10 documents insérés dans mydb.users
2026-01-29 10:01:17 - pipeline - INFO - === Pipeline terminé avec succès: 10 documents insérés ===
```

### Validation Pydantic en action

Si des données invalides sont détectées, elles sont automatiquement filtrées :

```
2026-01-29 10:01:16 - pipeline - WARNING - Utilisateur invalide ignoré (ID: 5): 1 validation error for RawUser
email
  value is not a valid email address
```

Le pipeline continue son exécution en ignorant les données invalides, assurant ainsi la robustesse du système.


## �🔒 Sécurité

- ⚠️ Ne committez **jamais** votre fichier `.env` dans Git
- Utilisez des variables d'environnement pour toutes les informations sensibles
- Pour la production, ajoutez une authentification et une validation des données

## 🚀 Améliorations possibles

- [ ] Ajouter une gestion des doublons (upsert)
- [ ] Implémenter une pagination pour `/users`
- [ ] Ajouter des tests unitaires et d'intégration
- [ ] Utiliser Motor pour une connexion MongoDB asynchrone
- [ ] Implémenter un système de retry en cas d'échec
- [ ] Ajouter une authentification JWT
- [ ] Créer un dashboard de monitoring
- [ ] Exporter les logs vers un système centralisé (ELK, Datadog)
- [ ] Ajouter des métriques de performance (temps d'exécution par étape)

## 📝 Licence

Ce projet est à usage éducatif et de démonstration.

## 👤 Auteur

Christophe Thibault

---

**Note** : Ce projet utilise l'API publique [JSONPlaceholder](https://jsonplaceholder.typicode.com/) pour la démonstration.
