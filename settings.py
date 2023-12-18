from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

DEBUG = config('DEBUG', cast=bool, default=False)
SECRET_KEY = config('SECRET_KEY', cast=Secret)

DATABASE_URL = config('DATABASE_URL')
