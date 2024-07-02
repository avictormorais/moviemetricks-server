from pymongo import MongoClient
from bson import ObjectId
import requests

class Playlist:
    @staticmethod
    def create_playlist(user_id, name, db):
        try:
            playlists_collection = db.playlists
            new_playlist = {
                "name": name,
                "user_id": user_id,
                "media": []
            }
            result = playlists_collection.insert_one(new_playlist)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating Playlist: {e}")
            return None

    @staticmethod
    def get_playlist_by_id(playlist_id, db):
        try:
            playlists_collection = db.playlists
            playlist = playlists_collection.find_one({"_id": ObjectId(playlist_id)})
            return playlist
        except Exception as e:
            print(f"Error getting playlist by id: {e}")
            return None

    @staticmethod
    def add_to_playlist(playlist_id, user_id, tmdb_id, media_type, api_key, db):
        try:
            playlist = Playlist.get_playlist_by_id(playlist_id, db)
            if playlist and playlist["user_id"] == user_id:
                media_details = Playlist.get_media_details(tmdb_id, media_type, api_key)
                if media_details:
                    print(media_details)
                    playlists_collection = db.playlists
                    result = playlists_collection.update_one(
                        {"_id": ObjectId(playlist_id)},
                        {"$addToSet": {"media": media_details}}
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
    def remove_from_playlist(playlist_id, user_id, tmdb_id, media_type, db):
        try:
            playlist = Playlist.get_playlist_by_id(playlist_id, db)
            if playlist and playlist["user_id"] == user_id:
                playlists_collection = db.playlists
                result = playlists_collection.update_one(
                    {"_id": ObjectId(playlist_id)},
                    {"$pull": {"media": {"tmdb_id": tmdb_id, "media_type": media_type}}}
                )
                return result.modified_count > 0
            else:
                return False
        except Exception as e:
            print(f"Error removing media from playlist: {e}")
            return False

    @staticmethod
    def get_playlists_by_user(user_id, db):
        try:
            playlists_collection = db.playlists
            playlists = playlists_collection.find({"user_id": user_id})
            result = []
            for playlist in playlists:
                playlist['_id'] = str(playlist['_id'])
                result.append(playlist)
            return result
        except Exception as e:
            print(f"Error getting playlists by user: {e}")
            return []

    @staticmethod
    def delete_playlist(playlist_id, user_id, db):
        try:
            playlists_collection = db.playlists
            result = playlists_collection.delete_one({"_id": ObjectId(playlist_id), "user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False
        
    @staticmethod
    def get_media_details(tmdb_id, media_type, api_key):
        try:
            response = requests.get(f'https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=pt-br')
            data = response.json()
            return {
                "tmdb_id": tmdb_id,
                "media_type": media_type,
                "title": data.get("title") or data.get("name"),
                "poster_path": data.get("poster_path") or "N/A",
                "vote_average": data.get("vote_average") or 0,
                "release_date": data.get("release_date") or data.get("first_air_date")
            }
        except Exception as e:
            print(f"Error getting media details: {e}")
            return None