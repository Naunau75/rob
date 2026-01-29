import httpx
import os
import logging
from typing import List
from pymongo import MongoClient
from dotenv import load_dotenv
from pydantic import ValidationError

from models import RawUser, TransformedUser, PipelineResult

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

class UserPipeline:
    def __init__(self) -> None:
        # Configuration MongoDB
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DB_NAME")
        self.col_name = os.getenv("COLLECTION_NAME")
        self.api_url = "https://jsonplaceholder.typicode.com/users"

    async def extract(self) -> List[RawUser]:
        """Étape 1: Faire le call API (Asynchrone)"""
        logger.info("Début de l'extraction des données depuis l'API")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url)
                response.raise_for_status()  # Lève une erreur si le call échoue
                data = response.json()
                logger.info(f"{len(data)} utilisateurs récupérés depuis {self.api_url}")
                
                # Validation avec Pydantic
                validated_users = []
                for user_data in data:
                    try:
                        validated_user = RawUser(**user_data)
                        validated_users.append(validated_user)
                    except ValidationError as e:
                        logger.warning(f"Utilisateur invalide ignoré (ID: {user_data.get('id', 'unknown')}): {e}")
                        continue
                
                logger.info(f"{len(validated_users)} utilisateurs validés sur {len(data)}")
                return validated_users
        except httpx.HTTPError as e:
            logger.error(f"Erreur lors de l'extraction des données: {e}")
            raise

    def transform(self, raw_data: List[RawUser]) -> List[TransformedUser]:
        """Étape 2: Formater les données"""
        logger.info(f"Début de la transformation de {len(raw_data)} utilisateurs")
        processed_data = []
        
        for user in raw_data:
            try:
                # Transformation avec validation Pydantic
                transformed_user = TransformedUser(
                    external_id=user.id,
                    full_name=user.name.upper(),
                    email=user.email.lower(),
                    location={
                        "city": user.address.city,
                        "geo": user.address.geo.model_dump()
                    },
                    company_name=user.company.name,
                    pipeline_source="Robyn-ETL"
                )
                processed_data.append(transformed_user)
            except ValidationError as e:
                logger.error(f"Erreur de validation pour l'utilisateur {user.id}: {e}")
                continue
        
        logger.info(f"Transformation terminée: {len(processed_data)} utilisateurs traités")
        return processed_data

    def load(self, data: List[TransformedUser]) -> int | str:
        """Étape 3: Stocker dans MongoDB"""
        logger.info("Début du chargement des données dans MongoDB")
        if not data:
            logger.warning("Aucune donnée à charger")
            return "Aucune donnée à charger."

        # Connexion au client (Pymongo est synchrone par défaut, ce qui est ok ici)
        # Pour de la très haute perf, on utiliserait 'motor', mais restons simple.
        client = MongoClient(self.mongo_uri)
        db = client[self.db_name]
        collection = db[self.col_name]

        # Convertir les modèles Pydantic en dictionnaires pour MongoDB
        mongo_documents = [user.to_mongo_dict() for user in data]

        # On utilise insert_many pour l'efficacité
        # Optionnel: On pourrait vérifier les doublons avant, mais ici on insère tout
        try:
            result = collection.insert_many(mongo_documents)
            client.close()
            logger.info(f"Succès: {len(result.inserted_ids)} documents insérés dans {self.db_name}.{self.col_name}")
            return len(result.inserted_ids)
        except Exception as e:
            client.close()
            logger.error(f"Erreur lors de l'insertion dans MongoDB: {e}")
            raise

    async def run(self) -> PipelineResult:
        """Orchestre tout le pipeline"""
        logger.info("=== Démarrage du pipeline ETL ===")
        try:
            raw_users = await self.extract()
            clean_users = self.transform(raw_users)
            count = self.load(clean_users)
            logger.info(f"=== Pipeline terminé avec succès: {count} documents insérés ===")
            
            return PipelineResult(
                status="success",
                inserted_count=count if isinstance(count, int) else 0,
                message=f"{count} utilisateurs traités avec succès"
            )
        except Exception as e:
            logger.error(f"=== Échec du pipeline: {e} ===")
            raise