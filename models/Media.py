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