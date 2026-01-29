"""
Modèles Pydantic pour la validation des données du pipeline ETL
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Dict


# Modèles pour les données brutes de l'API JSONPlaceholder
class GeoLocation(BaseModel):
    """Coordonnées géographiques"""
    lat: str
    lng: str


class Address(BaseModel):
    """Adresse d'un utilisateur"""
    street: str
    suite: str
    city: str
    zipcode: str
    geo: GeoLocation


class Company(BaseModel):
    """Entreprise d'un utilisateur"""
    name: str
    catchPhrase: str
    bs: str


class RawUser(BaseModel):
    """Utilisateur brut provenant de l'API JSONPlaceholder"""
    id: int
    name: str
    username: str
    email: EmailStr
    address: Address
    phone: str
    website: str
    company: Company

    class Config:
        # Permet d'accepter des champs supplémentaires sans erreur
        extra = "ignore"


# Modèles pour les données transformées (stockage MongoDB)
class Location(BaseModel):
    """Localisation simplifiée pour MongoDB"""
    city: str
    geo: Dict[str, str]


class TransformedUser(BaseModel):
    """Utilisateur transformé prêt pour MongoDB"""
    external_id: int = Field(..., description="ID de l'utilisateur dans l'API source")
    full_name: str = Field(..., min_length=1, description="Nom complet en majuscules")
    email: EmailStr = Field(..., description="Email en minuscules")
    location: Location
    company_name: str
    pipeline_source: str = Field(default="Robyn-ETL", description="Source du pipeline")

    @field_validator('full_name')
    @classmethod
    def validate_uppercase(cls, v: str) -> str:
        """Valide que le nom est bien en majuscules"""
        if not v.isupper():
            raise ValueError("Le nom doit être en majuscules")
        return v

    @field_validator('email')
    @classmethod
    def validate_lowercase(cls, v: str) -> str:
        """Valide que l'email est bien en minuscules"""
        if v != v.lower():
            raise ValueError("L'email doit être en minuscules")
        return v

    def to_mongo_dict(self) -> dict:
        """Convertit le modèle en dictionnaire pour MongoDB"""
        return self.model_dump(by_alias=True)


# Modèle pour la réponse du pipeline
class PipelineResult(BaseModel):
    """Résultat de l'exécution du pipeline"""
    status: str = Field(..., pattern="^(success|error)$")
    inserted_count: int = Field(..., ge=0, description="Nombre de documents insérés")
    message: str | None = Field(default=None, description="Message optionnel")
