# Rob - API ETL avec Robyn et MongoDB

Une API ETL (Extract, Transform, Load) moderne et performante construite avec [Robyn](https://github.com/sparckles/robyn) et MongoDB. Ce projet démontre comment créer un pipeline de données asynchrone pour extraire des données d'une API externe, les transformer et les stocker dans MongoDB.

## 🚀 Fonctionnalités

- **Pipeline ETL asynchrone** : Extraction, transformation et chargement de données
- **API REST rapide** : Propulsée par Robyn, un framework web Python ultra-rapide
- **Stockage MongoDB** : Persistance des données avec support MongoDB Atlas
- **Architecture modulaire** : Séparation claire entre le pipeline et l'API
- **Gestion d'environnement** : Configuration via variables d'environnement

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
  "inserted_count": 10
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
├── pyproject.toml       # Configuration du projet et dépendances
├── README.md            # Documentation
├── .env                 # Variables d'environnement (à créer)
└── .gitignore          # Fichiers à ignorer par Git
```

## 🔧 Architecture

### Pipeline ETL (`pipeline.py`)

La classe `UserPipeline` implémente le pattern ETL classique :

1. **Extract** : Appel asynchrone à l'API JSONPlaceholder avec `httpx`
2. **Transform** : 
   - Normalisation des noms (majuscules)
   - Normalisation des emails (minuscules)
   - Aplatissement de la structure des données
   - Ajout de métadonnées (source du pipeline)
3. **Load** : Insertion en masse dans MongoDB avec `pymongo`

### API REST (`main.py`)

- Framework : **Robyn** (async, haute performance)
- Routes :
  - `/` : Page d'accueil
  - `/run-pipeline` : Déclenchement du pipeline
  - `/users` : Consultation des données

## 📦 Dépendances

- **robyn** (>=0.76.0) : Framework web asynchrone
- **pymongo[srv]** (>=4.16.0) : Driver MongoDB
- **httpx** (>=0.28.1) : Client HTTP asynchrone
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

## 🔒 Sécurité

- ⚠️ Ne committez **jamais** votre fichier `.env` dans Git
- Utilisez des variables d'environnement pour toutes les informations sensibles
- Pour la production, ajoutez une authentification et une validation des données

## 🚀 Améliorations possibles

- [ ] Ajouter une gestion des doublons (upsert)
- [ ] Implémenter une pagination pour `/users`
- [ ] Ajouter des tests unitaires et d'intégration
- [ ] Utiliser Motor pour une connexion MongoDB asynchrone
- [ ] Ajouter un système de logs structurés
- [ ] Implémenter un système de retry en cas d'échec
- [ ] Ajouter une authentification JWT
- [ ] Créer un dashboard de monitoring

## 📝 Licence

Ce projet est à usage éducatif et de démonstration.

## 👤 Auteur

Christophe Thibault

---

**Note** : Ce projet utilise l'API publique [JSONPlaceholder](https://jsonplaceholder.typicode.com/) pour la démonstration.
