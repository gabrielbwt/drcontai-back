from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "production"
    pluggy_client_id: str = ""
    pluggy_client_secret: str = ""
    database_url: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")