from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Workflow Engine"
    debug: bool = True

    class Config:
        env_prefix = "WF_"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()
