
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY','dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL','sqlite:///bir_kun_bir_hikoya.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME','brainn_hr')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD','admin123')
    ADMIN_HIDDEN_URL = os.getenv('ADMIN_URL','/brainn-hr-admin-2026')
