
import json
from bson import ObjectId, json_util
from flask import jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import requests



load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
api_key= os.getenv('TMDB_KEY')





class MediaAPI:
    @staticmethod
    def get_media_details(tmdb_id, media_type, api_key):
        base_url = "https://api.themoviedb.org/3/"
        url = f"{base_url}{media_type}/{tmdb_id}?api_key={api_key}&language=pt-BR"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data.")
            return None

    @staticmethod
    def add_media_to_database(media_details, media_type, db):
        if media_details:
            if(media_type == "movie"):
                media_data = {
                    "tmdb_id": media_details["id"],  
                    "poster_path": media_details["poster_path"] or '',
                    "title": media_details["title"] or media_details["name"],
                    "vote_average": media_details["vote_average"] or '?',
                    "release_date": media_details["release_date"] or media_details["first_air_date"],
                    "media_type": media_type,
                    "comments": []
                }
            else:
                media_data = {
                "tmdb_id": media_details["id"],  
                "poster_path": media_details["poster_path"] or '',
                "title": media_details["name"],
                "vote_average": media_details["vote_average"] or '?',
                "release_date": media_details["first_air_date"],
                "media_type": media_type,
                "comments": []
                }
            collection = db["media"]
            result = collection.insert_one(media_data)
            print("Media added to database successfully.")
            return result
        else:
            print("Failed to add media to database.")
            return None

    
    @staticmethod
    def get_or_create_media(tmdb_id, media_type, api_key):  
        collection = db["media"]
        existing_media = collection.find_one({"tmdb_id": int(tmdb_id), "media_type": media_type})  
        if existing_media:
            print("Media already exists in database.")
            return existing_media
        else:
            media_details = MediaAPI.get_media_details(tmdb_id, media_type, api_key)
            if media_details:
                MediaAPI.add_media_to_database(media_details, media_type, db)
                return media_details
            else:
                return None


    @staticmethod
    def get_media_comments(tmdb_id, db):
        collection = db["media"]
        media = collection.find_one({"tmdb_id": tmdb_id}, {"comments": 1})
        if media:
            comments = media.get("comments", [])
            return comments
        else:
            print("Media not found in the database.")
            return None

    @staticmethod
    def get_all_media(db):
        collection = db["media"]
        all_media = collection.find({}, {"_id": 0}) 
        return list(all_media)
    


    @staticmethod
    def add_comment_to_media(tmdb_id, comment_id, review, user_id, media_type, media_title, is_spoiler, stars):
     try:
        media_details = MediaAPI.get_or_create_media(tmdb_id, media_type, api_key)

        if not media_details:
            print("Failed to get media details")
            return False

        collection = db["media"]
        media = collection.find_one({"tmdb_id": tmdb_id})
        if not media:
            print("Media not found")
            return False

        if media_details:
            result = collection.update_one(
                {"tmdb_id": tmdb_id},
                {
                    "$push": {
                        "comments": {
                            "comment_id": ObjectId(comment_id),  
                            "review": review,
                            "user_id": ObjectId(user_id),  
                            "media_type": media_type,
                            "media_title": media_title,
                            "is_spoiler": is_spoiler,
                            "stars": stars
                        }
                    }
                }
            )

            if result.modified_count > 0:
                print("Comment added to media successfully")
                return True
            else:
                print("Failed to add comment to media")
                return False
        else:
            print("Failed to get media details")
            return False
     except Exception as e:
        print(f"Error adding comment to media: {e}")
        return False


    @staticmethod
    def get_all_media_comments():
        try:
            collection = db["media"]
            media_with_comments = collection.find({"comments": {"$exists": True, "$ne": []}})

            media_list = [json.loads(json_util.dumps(media)) for media in media_with_comments]

            return media_list
        except Exception as e:
            print(f"Error retrieving media with comments: {e}")
            return None
        
    @staticmethod
    def get_media_comment(tmdb_id, media_type):
     try:
        collection = db["media"]
        media_with_comments = collection.find_one({"tmdb_id": tmdb_id, "media_type": media_type})

        if media_with_comments:
            return json.loads(json_util.dumps([media_with_comments]))
        else:
            return None
     except Exception as e:
        print(f"Error retrieving media with comments: {e}")
        return None
     

