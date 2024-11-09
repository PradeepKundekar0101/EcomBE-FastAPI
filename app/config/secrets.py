from dotenv import load_dotenv
import os

load_dotenv()
DB_URL= os.environ.get("DB_URL")
JWT_SECRET =  os.environ.get("JWT_SECRET")