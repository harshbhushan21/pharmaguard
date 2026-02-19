"""Configuration management for PharmaGuard backend."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Any


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )
    
    # OpenAI API Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> str:
        """Parse CORS origins - keep as string, will be split when used."""
        if isinstance(v, list):
            return ','.join(v)
        if isinstance(v, str):
            return v
        return "http://localhost:3000,http://localhost:5173"
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
    
    # Application Settings
    max_file_size_mb: int = 5
    supported_drugs: List[str] = [
        "CODEINE",
        "WARFARIN",
        "CLOPIDOGREL",
        "SIMVASTATIN",
        "AZATHIOPRINE",
        "FLUOROURACIL"
    ]
    
    # Target genes for pharmacogenomics analysis
    target_genes: List[str] = [
        "CYP2D6",
        "CYP2C19",
        "CYP2C9",
        "SLCO1B1",
        "TPMT",
        "DPYD"
    ]


settings = Settings()
