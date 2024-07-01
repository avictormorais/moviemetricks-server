from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.Media import MediaAPI
from pymongo import MongoClient
from bson import ObjectId, json_util
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
api_key = os.getenv('TMDB_KEY')

class Comment:
    @staticmethod
    def create_comment(user_id, username, media_id, media_type, review, is_spoiler, stars, title, userRole):
        try:
            collection = db["comment"]

            new_comment = {
                "user_id": ObjectId(user_id),
                "username": username,
                "media_id": media_id,
                "media_type": media_type,
                "review": review,
                "stars": stars,
                "is_spoiler": is_spoiler,
                "title": title,
                "userRole": userRole
            }
            
            result = collection.insert_one(new_comment)
            print("Comment added successful, ID:", result.inserted_id)
            return result.inserted_id
        except Exception as e:
            print("Error added comment:", e)
            return None

    @staticmethod
    @jwt_required()
    def update_comment(comment_id, review, is_spoiler, stars):
        try:
            collection = db["comment"]
            result = collection.update_one({"_id": ObjectId(comment_id)}, {"$set": {"review": review, "is_spoiler": is_spoiler, "stars": stars}})
            
            if result.modified_count == 1:
                print("Comment updated successfully")
                return True
            else:
                print("Comment not found or not updated")
                return False
        except Exception as e:
            print("Error updating comment:", e)
            return None

    @staticmethod
    @jwt_required()
    def delete_comment(comment_id):
        try:
            collection = db["comment"]
            result = collection.delete_one({"_id": ObjectId(comment_id)})
            if result.deleted_count == 1:
                print("Comment deleted successfully")
                return True
            else:
                print("Comment not found or not deleted")
                return False
        except Exception as e:
            print("Error deleting comment:", e)
            return None

    @staticmethod
    def get_comment(comment_id):
        try:
            collection = db["comment"]
            comment = collection.find_one({"_id": ObjectId(comment_id)})
            
            if comment:
                return comment
            else:
                print("Comment not found")
                return None
        except Exception as e:
            print("Error retrieving comment:", e)
            return None