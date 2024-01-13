from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
SECRET_KEY = config("SECRET_KEY", cast=Secret)

DATABASE_URL = config("DATABASE_URL")
AUTH_ROLE = config("AUTH_ROLE")


EMAIL_INTERVAL = config("EMAIL_INTERVAL", cast=int)
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_USER = config("EMAIL_USER")
EMAIL_PASS = config("EMAIL_PASS")
