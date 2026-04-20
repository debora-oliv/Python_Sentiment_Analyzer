from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Define o nome, o tipo e, se aplicável, o valor padrão de cada variável para busca automatica no .env
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str
    redis_host: str = "redis"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False
    )

settings = Settings()