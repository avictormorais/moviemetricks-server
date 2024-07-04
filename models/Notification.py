from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

import requests

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))
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
                  if movie is None:
                      new_movie = {
                          "movieId": movieId,
                          "date": release_date
                      }
                      result = to_verify_movies_collection.insert_one(new_movie)
                      return str(result.inserted_id)
                  else:
                      if movie.get('date') == release_date:
                          return str(movie.get('_id'))
                      else:
                        movie.update({"date": release_date})
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