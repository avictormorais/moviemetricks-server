from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from bson import ObjectId
                    
load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database("Notification")
db_users = client.get_database(os.getenv("MONGODB_DBNAME"))
api_key = os.getenv('TMDB_KEY')

current_date = datetime.now().date()
to_verify_movies_collection = db.toVerifyMovies
to_notify_movies_collection = db.toNotifyMovies

class Notification:
    @staticmethod
    def create_or_get_movie(movieId):
        try:
            movie = to_verify_movies_collection.find_one({"movieId": movieId})
            url = f"https://api.themoviedb.org/3/movie/{movieId}/release_dates"
            parametros = {'api_key': api_key}
            response = requests.get(url, params=parametros)

            if response.status_code == 200:
                data = response.json()
                data.get('results').sort(key=lambda x: x.get('iso_3166_1'))
                brasil_release = next((result for result in data.get('results') if result.get('iso_3166_1') == 'BR'), None)
                if brasil_release:
                    release_date = brasil_release.get('release_dates')[0].get('release_date')
                    if release_date.find('T'):
                        release_date = release_date.split('T')[0]
                    if movie is None:
                        new_movie = {
                            "movieId": movieId,
                            "date": release_date,
                            "users_count": 0
                        }
                        result = to_verify_movies_collection.insert_one(new_movie)
                        return str(result.inserted_id)
                    else:
                        if movie.get('date') == release_date:
                            return str(movie.get('_id'))
                        else:
                            to_verify_movies_collection.update_one(
                                {"movieId": movieId},
                                {"$set": {"date": release_date}}
                            )
                            return str(movie.get('_id'))
            else:
                print(f"Error getting release date: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error creating or getting movie: {e}")
            return None

    @staticmethod
    def add_movie_to_notify(userId, movieId):
        try:
            movie = to_notify_movies_collection.find_one({"userId": userId, "movieId": movieId})
            if movie is None:
                new_movie = {
                    "userId": userId,
                    "movieId": movieId
                }
                result = to_notify_movies_collection.insert_one(new_movie)
                to_verify_movies_collection.update_one(
                    {"movieId": movieId},
                    {"$inc": {"users_count": 1}}
                )
                return str(result.inserted_id)
            else:
                return str(movie.get('_id'))
        except Exception as e:
            print(f"Error adding movie to notify: {e}")
            return None   

    @staticmethod
    def remove_movie_to_notify(userId, movieId):
        try:
            result = to_notify_movies_collection.delete_one({"userId": userId, "movieId": movieId})
            to_verify_movies_collection.update_one(
                {"movieId": movieId},
                {"$inc": {"users_count": -1}}
            )
            movie = to_verify_movies_collection.find_one({"movieId": movieId})
            if movie.get('users_count', 0) == 0:
                to_verify_movies_collection.delete_one({"movieId": movieId})
            return result.deleted_count
        except Exception as e:
            print(f"Error removing movie to notify: {e}")
            return None

    @staticmethod
    def get_movie_notification(userId, movieId):
        try:
            movie = to_notify_movies_collection.find_one({"userId": userId, "movieId": movieId})
            return movie
        except Exception as e:
            print(f"Error getting movie notification: {e}")
            return None
        
    @staticmethod
    def notify_users():
        try:
            current_date = str(datetime.now()).split(' ')[0]
            movies_to_notify = to_verify_movies_collection.find({"date": {"$eq": current_date}})
            for movie in movies_to_notify:
                notifications = list(to_notify_movies_collection.find({"movieId": movie["movieId"]}))
                for notification in notifications:
                    userId = notification["userId"]
                    
                    notification_obj = {
                        "id": str(ObjectId()),
                        "type": 'release',
                        "contentId": movie["movieId"],
                        "contentType": 'movie',
                        "date": current_date
                    }
                    
                    db_users.users.update_one(
                        {"_id": ObjectId(userId)},
                        {"$push": {"notifications": notification_obj}}
                    )
                    to_notify_movies_collection.delete_one({"_id": notification["_id"]})
                to_verify_movies_collection.delete_one({"_id": movie["_id"]})
        
        except Exception as e:
            print(f"Error notifying users: {e}")
            
    @staticmethod
    def get_user_notifications(userId):
        try:
            user = db_users.users.find_one({"_id": ObjectId(userId)})
            return user.get("notifications", [])
        except Exception as e:
            print(f"Error getting user notifications: {e}")
            return None