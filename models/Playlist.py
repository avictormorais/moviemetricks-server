
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from models.Media import MediaAPI

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
api_key= os.getenv('TMDB_KEY')


class Playlist:
    @staticmethod
    def create_playlist_model(userId, name):
        try:
            playlists_collection = db.playlists
            new_playlist = {
                "name": name,
                "userId": userId,
                "media": []
            }
            result = playlists_collection.insert_one(new_playlist)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating Playlist: {e}")
            return None

    @staticmethod
    def get_playlist_by_id_model(playlistId):
        try:
            playlists_collection = db.playlists
            playlist = playlists_collection.find_one({"_id": playlistId})
            return playlist
        except Exception as e:
            print(f"Error getting playlist by id: {e}")
            return None
    

    @staticmethod
    def add_to_playlist(playlist_id, tmdb_id, media_type, api_key):
     try:
        playlist = Playlist.get_playlist_by_id_model(playlist_id)
        if playlist:
            media_details = MediaAPI.get_or_create_media(tmdb_id, media_type, api_key)
            if media_details:
                playlists_collection = db.playlists
                result = playlists_collection.update_one(
                    {"_id": playlist_id},
                    {"$addToSet": {
                        "media": {
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
        print(f"Error adding media to playlist: {e}")
        return False
    

    @staticmethod
    def remove_from_playlist(playlist_id, tmdb_id, media_type):
     try:
        playlists_collection = db.playlists
        result = playlists_collection.update_one(
            {"_id": playlist_id},
            {"$pull": {
                "media": {
                    "tmdb_id": tmdb_id,
                    "media_type": media_type
                }
            }}
        )
        return result.modified_count > 0
     except Exception as e:
        print(f"Error removing media from playlist: {e}")
        return False

