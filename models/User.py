
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from models.Media import MediaAPI
from flask_jwt_extended import jwt_required, get_jwt_identity

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
api_key= os.getenv('TMDB_KEY')

class User:
    @staticmethod
    def create_user_model(email, username,role, hashed_password_base64):
        try:
            users_collection = db.users
            new_user = {
                "username": username,
                "email": email,
                "role": role,
                "password": hashed_password_base64,
                "watched": [],
                "watched_episodes": []
            }
            result = users_collection.insert_one(new_user)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    def get_user_by_username_model(username):
        users_collection = db.users
        user = users_collection.find_one({"username": username})
        return user

    @staticmethod
    def get_user_by_email_model(email):
        try:
            users_collection = db.users
            user = users_collection.find_one({"email": email})
            return user
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            return None

    @staticmethod
    def get_user_by_id_model(id):
        try:
            users_collection = db.users
            user = users_collection.find_one({"_id": ObjectId(id)})
            return user
        except Exception as e:
            print(f"Error retrieving user by ID: {e}")
            return None

    @staticmethod
    def update_user(user_id, updated_fields):
        try:
            users_collection = db.users
            result = users_collection.update_many({"_id": ObjectId(user_id)}, {"$set": updated_fields})
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    @staticmethod
    def delete_account_model(user_id):
        try:
            users_collection = db.users
            result = users_collection.find_one_and_delete({"_id": ObjectId(user_id)})
            return result is not None
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    @staticmethod
    def add_watched_list(tmdb_id, media_type, api_key):
      try:
        user_id = get_jwt_identity()
        if user_id:
            media_details = MediaAPI.get_media_details(tmdb_id, media_type, api_key)
            if media_details:
                users_collection = db.users
                result = users_collection.update_one(
                    {"_id":ObjectId(user_id)},
                    {"$addToSet": {
                        "watched": {
                            "tmdb_id": tmdb_id,
                            "media_type": media_type,
                            "title": media_details.get("title") or media_details.get("name"),
                            "poster_path": media_details.get("poster_path") or "N/A",
                            "vote_average": media_details.get("vote_average") or 0,
                            "release_date": media_details.get("release_date") or media_details.get("first_air_date")
                        }
                    }}
                )
                return result.modified_count > 0
            else:
                return False 
        else:
            return False  
      except Exception as e:
        print(f"Error adding movie to watched list: {e}")
        return False
      
    @staticmethod
    @jwt_required() 
    def delete_from_watched_list(tmdb_id, media_type, api_key):
        try:
            user_id = get_jwt_identity()
            user = User.get_user_by_id_model(user_id)
            if user:
                media_details = MediaAPI.get_media_details(tmdb_id, media_type, api_key)
                if media_details:
                    users_collection = db.users
                    result = users_collection.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$pull": {"watched": {"tmdb_id": tmdb_id, "media_type": media_type}}}
                    )
                    return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting movie from watched list: {e}")
        return False
    
    def update_user_role(user_id, new_role):
        try:
            users_collection = db.users
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"role": new_role}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False