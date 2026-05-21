import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    def __init__(self):
        missing = [
            var for var in ("DB_NAME", "DB_USER", "DB_PASSWORD")
            if not getattr(self, var)
        ]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please check your .env file."
            )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Config initialization — akan raise error jelas jika .env tidak lengkap
config = Config()
