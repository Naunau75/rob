from robyn import Robyn, jsonify
from robyn.types import Request
from pipeline import UserPipeline
from pymongo import MongoClient
import os
import logging
from typing import Any
from dotenv import load_dotenv

load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Robyn(__file__)

# Instance du pipeline
pipeline = UserPipeline()

@app.get("/")
async def h(request: Request) -> str:
    logger.info("Requête reçue sur la route racine /")
    return "Bienvenue sur l'API ETL ! Fais un POST sur /run-pipeline pour lancer."

# Route 1 : Déclencher le pipeline
@app.post("/run-pipeline")
async def trigger_pipeline(request: Request) -> Any:
    logger.info("Requête POST reçue sur /run-pipeline - Démarrage du pipeline")
    try:
        # Appel de la méthode run() de notre classe Pipeline
        result = await pipeline.run()
        # Convertir le modèle Pydantic en dict pour jsonify
        logger.info(f"Pipeline exécuté avec succès: {result}")
        return jsonify(result.model_dump())
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du pipeline: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)})

# Route 2 : Consulter les données (Lecture simple depuis Mongo)
@app.get("/users")
async def get_users(request: Request) -> Any:
    logger.info("Requête GET reçue sur /users")
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client[os.getenv("DB_NAME")]
        col = db[os.getenv("COLLECTION_NAME")]
        
        # Récupérer les 10 derniers, sans l'ID technique de Mongo (pour éviter les erreurs de sérialisation JSON)
        users = list(col.find({}, {"_id": 0}).limit(10))
        client.close()
        
        logger.info(f"{len(users)} utilisateurs récupérés depuis MongoDB")
        return jsonify(users)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}", exc_info=True)
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    logger.info("Démarrage de l'application Robyn sur le port 8080")
    app.start(port=8080)