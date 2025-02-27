TOKEN = '7101517441:AAFzmV5NDxLKgvr33zDvew3uncw642kQL10'

from pydantic_settings import BaseSettings, SettingsConfigDict



class BotConfig:
    def __init__(self, admin_ids, welcome_message) -> None:
        self.admin_ids = admin_ids
        self.welcome_message = welcome_message




class Settings(BaseSettings):
    token: str
    db_url: str
    db_echo: bool = True
        
    model_config = SettingsConfigDict(
        env_file = ".env"
    )

settings = Settings()




