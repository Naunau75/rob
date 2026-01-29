import httpx
import os
from typing import Any, Dict, List
from pymongo import MongoClient
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class UserPipeline:
    def __init__(self) -> None:
        # Configuration MongoDB
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DB_NAME")
        self.col_name = os.getenv("COLLECTION_NAME")
        self.api_url = "https://jsonplaceholder.typicode.com/users"

    async def extract(self) -> List[Dict[str, Any]]:
        """Étape 1: Faire le call API (Asynchrone)"""
        print("--- Début de l'extraction ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url)
            response.raise_for_status() # Lève une erreur si le call échoue
            data = response.json()
            print(f"{len(data)} utilisateurs récupérés.")
            return data

    def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Étape 2: Formater les données"""
        print("--- Début de la transformation ---")
        processed_data = []
        
        for user in raw_data:
            # On simplifie la structure : on veut juste nom, email, et ville
            # L'API renvoie l'adresse imbriquée, on va l'aplatir.
            transformed_user = {
                "external_id": user["id"],
                "full_name": user["name"].upper(), # Exemple de transfo : tout en majuscule
                "email": user["email"].lower(),
                "location": {
                    "city": user["address"]["city"],
                    "geo": user["address"]["geo"]
                },
                "company_name": user["company"]["name"],
                "pipeline_source": "Robyn-ETL" # Tag pour savoir d'où ça vient
            }
            processed_data.append(transformed_user)
            
        return processed_data

    def load(self, data: List[Dict[str, Any]]) -> int | str:
        """Étape 3: Stocker dans MongoDB"""
        print("--- Début du chargement ---")
        if not data:
            return "Aucune donnée à charger."

        # Connexion au client (Pymongo est synchrone par défaut, ce qui est ok ici)
        # Pour de la très haute perf, on utiliserait 'motor', mais restons simple.
        client = MongoClient(self.mongo_uri)
        db = client[self.db_name]
        collection = db[self.col_name]

        # On utilise insert_many pour l'efficacité
        # Optionnel: On pourrait vérifier les doublons avant, mais ici on insère tout
        result = collection.insert_many(data)
        client.close()
        
        print(f"Succès : {len(result.inserted_ids)} documents insérés.")
        return len(result.inserted_ids)

    async def run(self) -> Dict[str, Any]:
        """Orchestre tout le pipeline"""
        raw_users = await self.extract()
        clean_users = self.transform(raw_users)
        count = self.load(clean_users)
        return {"status": "success", "inserted_count": count}