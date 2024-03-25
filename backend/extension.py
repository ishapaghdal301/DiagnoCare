from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import os 
from dotenv import load_dotenv

load_dotenv()
# MONGODB URI
MONGO_URI = os.getenv("MONGO_URI")
mongo = MongoClient(MONGO_URI)
db = mongo.get_database()
backend = db['sdp_backend']
auth_collection = backend['auth']
store_collection = backend['store']
patient_collection = backend['patient']
appointment_collection = backend['appointment']
doctor_collection = backend['doctor']
jwt = JWTManager()




