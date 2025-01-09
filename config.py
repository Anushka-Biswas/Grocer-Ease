import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    MONGODB_SETTINGS = {
        'db': 'grocer_ease',
        'host': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/grocer_ease')
    }
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')
    if not SERPAPI_API_KEY:
        raise ValueError("No SERPAPI_API_KEY set for price optimization")

    # Ensure the upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

