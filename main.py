from robyn import Robyn, jsonify
from robyn.types import Request
from pipeline import UserPipeline
from pymongo import MongoClient
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

app = Robyn(__file__)

# Instance du pipeline
pipeline = UserPipeline()

@app.get("/")
async def h(request: Request) -> str:
    return "Bienvenue sur l'API ETL ! Fais un POST sur /run-pipeline pour lancer."

# Route 1 : Déclencher le pipeline
@app.post("/run-pipeline")
async def trigger_pipeline(request: Request) -> Any:
    try:
        # Appel de la méthode run() de notre classe Pipeline
        result = await pipeline.run()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Route 2 : Consulter les données (Lecture simple depuis Mongo)
@app.get("/users")
async def get_users(request: Request) -> Any:
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client[os.getenv("DB_NAME")]
        col = db[os.getenv("COLLECTION_NAME")]
        
        # Récupérer les 10 derniers, sans l'ID technique de Mongo (pour éviter les erreurs de sérialisation JSON)
        users = list(col.find({}, {"_id": 0}).limit(10))
        client.close()
        
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.start(port=8080)