from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")


settings = Settings()