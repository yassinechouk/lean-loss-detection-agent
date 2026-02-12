"""
Configuration globale de l'application avec pydantic-settings.
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration de l'application."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Configuration OpenAI
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.2
    
    # Configuration des données
    data_dir: str = "data/synthetic"
    output_dir: str = "data/output"
    
    def is_api_configured(self) -> bool:
        """Vérifie si une clé API est configurée."""
        return self.openai_api_key is not None and len(self.openai_api_key) > 0
    
    def get_data_path(self) -> Path:
        """Retourne le chemin absolu du répertoire de données."""
        return Path(self.data_dir).resolve()
    
    def get_output_path(self) -> Path:
        """Retourne le chemin absolu du répertoire de sortie."""
        path = Path(self.output_dir).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne l'instance singleton de la configuration.
    Utilise lru_cache pour s'assurer qu'il n'y a qu'une seule instance.
    
    Returns:
        Instance de Settings
    """
    return Settings()
