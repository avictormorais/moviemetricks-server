from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from bson import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database("Notification")
db_users = client.get_database(os.getenv("MONGODB_DBNAME"))
api_key = os.getenv('TMDB_KEY')

current_date = datetime.now().date()
to_verify_movies_collection = db.toVerifyMovies
to_notify_movies_collection = db.toNotifyMovies
to_verify_series_collection = db.toVerifySeries
to_notify_series_collection = db.toNotifySeries

class Notification:
    @staticmethod
    def create_or_get_movie(movieId):
        try:
            movie = to_verify_movies_collection.find_one({"movieId": movieId})
            url = f"https://api.themoviedb.org/3/movie/{movieId}"
            parametros = {'api_key': api_key, 'language': 'pt-BR'}
            response = requests.get(url, params=parametros)
            if response.status_code == 200:
                data = response.json()
                release_dates_url = f"https://api.themoviedb.org/3/movie/{movieId}/release_dates"
                release_dates_response = requests.get(release_dates_url, params={'api_key': api_key})
                if release_dates_response.status_code == 200:
                    release_dates_data = release_dates_response.json()
                    release_dates_data.get('results').sort(key=lambda x: x.get('iso_3166_1'))
                    brasil_release = next((result for result in release_dates_data.get('results') if result.get('iso_3166_1') == 'BR'), None)
                    if brasil_release:
                        release_date = brasil_release.get('release_dates')[0].get('release_date')
                        if release_date.find('T'):
                            release_date = release_date.split('T')[0]
                        title = data.get('title')
                        if movie is None:
                            new_movie = {
                                "movieId": movieId,
                                "date": release_date,
                                "title": title,
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
                                    {"$set": {"date": release_date, "title": title}}
                                )
                                return str(movie.get('_id'))
                else:
                    print(f"Error getting release date: {release_dates_response.status_code}")
                    return None
            else:
                print(f"Error getting movie details: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error creating or getting movie: {e}")
            return None
    
    @staticmethod
    def add_movie_to_notify(userId, movieId, sendEmail):
        try:
            movie = to_notify_movies_collection.find_one({"userId": userId, "movieId": movieId})
            if movie is None:
                new_movie = {
                    "userId": userId,
                    "movieId": movieId,
                    "sendEmail": sendEmail
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
    def create_or_get_series(seriesId):
        try:
            series = to_verify_series_collection.find_one({"serieId": seriesId})
            url = f"https://api.themoviedb.org/3/tv/{seriesId}"
            parametros = {'api_key': api_key, 'language': 'pt-BR'}
            response = requests.get(url, params=parametros)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "Ended" or data.get("status") == "Canceled":
                    return None
                release_date = data.get('next_episode_to_air')
                if release_date:
                    release_date = release_date.get('air_date')
                if series is None:
                    new_series = {
                        "serieId": seriesId,
                        "date": release_date,
                        "title": data.get("name"),
                        "users_count": 0
                    }
                    result = to_verify_series_collection.insert_one(new_series)
                    return str(result.inserted_id)
                else:
                    if series.get('date') == release_date:
                        return str(series.get('_id'))
                    else:
                        to_verify_series_collection.update_one(
                            {"serieId": seriesId},
                            {"$set": {"date": release_date}}
                        )
                        return str(series.get('_id'))
            else:
                print(f"Error getting release date: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error creating or getting series: {e}")
            return None

    @staticmethod
    def add_serie_to_notify(userId, seriesId, sendEmail):
        try:
            series = to_notify_series_collection.find_one({"userId": userId, "serieId": seriesId})
            if series is None:
                new_series = {
                    "userId": userId,
                    "serieId": seriesId,
                    "sendEmail": sendEmail
                }
                result = to_notify_series_collection.insert_one(new_series)
                to_verify_series_collection.update_one(
                    {"serieId": seriesId},
                    {"$inc": {"users_count": 1}}
                )
                return str(result.inserted_id)
            else:
                return str(series.get('_id'))
        except Exception as e:
            print(f"Error adding series to notify: {e}")
            return None

    @staticmethod
    def remove_serie_to_notify(userId, seriesId):
        try:
            result = to_notify_series_collection.delete_one({"userId": userId, "serieId": seriesId})
            to_verify_series_collection.update_one(
                {"serieId": seriesId},
                {"$inc": {"users_count": -1}}
            )
            series = to_verify_series_collection.find_one({"serieId": seriesId})
            if series.get('users_count', 0) == 0:
                to_verify_series_collection.delete_one({"serieId": seriesId})
            return result.deleted_count
        except Exception as e:
            print(f"Error removing series to notify: {e}")
            return None

    @staticmethod
    def get_serie_notification(userId, seriesId):
        try:
            series = to_notify_series_collection.find_one({"userId": userId, "serieId": seriesId})
            return series
        except Exception as e:
            print(f"Error getting series notification: {e}")
            return None

    @staticmethod
    def update_series_dates():
        try:
            current_date = str(datetime.now()).split(' ')[0]
            series_to_update = to_verify_series_collection.find({
                "$or": [
                    {"last_checked": {"$exists": False}},
                    {"last_checked": {"$lt": current_date}}
                ]
            })
            for series in series_to_update:
                seriesId = series["serieId"]
                url = f"https://api.themoviedb.org/3/tv/{seriesId}"
                parametros = {'api_key': api_key, 'language': 'pt-BR'}
                response = requests.get(url, params=parametros)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "Ended" or data.get("status") == "Canceled":
                        to_verify_series_collection.delete_one({"serieId": seriesId})
                        continue
                    release_date = data.get('next_episode_to_air')
                    if release_date:
                        release_date = release_date.get('air_date')
                        if series["date"] is None:
                            notifications = list(to_notify_series_collection.find({"serieId": series["serieId"]}))
                            for notification in notifications:
                                userId = notification["userId"]
                                notification_obj = {
                                    "id": str(ObjectId()),
                                    "type": 'new_release_date',
                                    "contentId": series["serieId"],
                                    "contentType": 'serie',
                                    "date": current_date,
                                    "title": series["title"],
                                    "new_date": release_date
                                }
                                db_users.users.update_one(
                                    {"_id": ObjectId(userId)},
                                    {"$push": {"notifications": notification_obj}}
                                )
                        to_verify_series_collection.update_one(
                            {"serieId": seriesId},
                            {"$set": {"date": release_date, "last_checked": current_date}}
                        )
                    else:
                        print(f"Release date not found for seriesId: {seriesId}")
                else:
                    print(f"Error fetching series details, status code: {response.status_code}")
        except Exception as e:
            print(f"Error updating series dates: {e}")

    @staticmethod
    def send_email(email, title, content_type, id):
        sender_email = os.getenv('SENDER_EMAIL')
        password = os.getenv('EMAIL_PASSWORD')
        receiver_email = email

        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = receiver_email

        if content_type == 'movie':
            msg['Subject'] = f"Filme {title} lançado!"
            with open('assets/filme.html', 'r', encoding='utf-8') as file:
                html = file.read()
                html = html.format(title=title, type='tv', id=id)
        else:
            msg['Subject'] = f"Novo episódio: {title}!"
            with open('assets/novo_ep.html', 'r', encoding='utf-8') as file:
                html = file.read()
                html = html.format(title=title, type='tv', id=id)

        part = MIMEText(html, 'html')
        msg.attach(part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    
    @staticmethod
    def notify_users():
        try:
            Notification.update_series_dates()
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
                        "title": movie["title"],
                        "date": current_date
                    }
                    db_users.users.update_one(
                        {"_id": ObjectId(userId)},
                        {"$push": {"notifications": notification_obj}}
                    )
                    user = db_users.users.find_one({"_id": ObjectId(userId)})
                    usermail = user.get("email")
                    if notification["sendEmail"]:
                        Notification.send_email(usermail, movie["title"], 'movie', movie["movieId"])
                    to_notify_movies_collection.delete_one({"_id": notification["_id"]})
                to_verify_movies_collection.delete_one({"_id": movie["_id"]})
            
            series_to_notify = to_verify_series_collection.find({"date": {"$eq": current_date}})
            for series in series_to_notify:
                notifications = list(to_notify_series_collection.find({"serieId": series["serieId"]}))
                for notification in notifications:
                    userId = notification["userId"]
                    notification_obj = {
                        "id": str(ObjectId()),
                        "type": 'release',
                        "contentId": series["serieId"],
                        "contentType": 'serie',
                        "title": series["title"],
                        "date": current_date
                    }
                    db_users.users.update_one(
                        {"_id": ObjectId(userId)},
                        {"$push": {"notifications": notification_obj}}
                    )
                    user = db_users.users.find_one({"_id": ObjectId(userId)})
                    usermail = user.get("email")
                    if notification["sendEmail"]:
                        Notification.send_email(usermail, series["title"], 'serie', series["serieId"])
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

    @staticmethod
    def remove_user_notifications(userId):
        try:
            result = db_users.users.update_one(
                {"_id": ObjectId(userId)},
                {"$set": {"notifications": []}}
            )
            return result.modified_count
        except Exception as e:
            print(f"Error removing user notifications: {e}")
            return None
        
    @staticmethod
    def remove_user_notification(userId, notificationId):
        try:
            result = db_users.users.update_one(
                {"_id": ObjectId(userId)},
                {"$pull": {"notifications": {"id": notificationId}}}
            )
            return result.modified_count
        except Exception as e:
            print(f"Error removing user notification: {e}")
            return None
        
    @staticmethod
    def get_user_notification(userId, notificationId):
        try:
            user = db_users.users.find_one({"_id": ObjectId(userId)})
            notifications = user.get("notifications", [])
            return next((notification for notification in notifications if notification.get("id") == notificationId), None)
        except Exception as e:
            print(f"Error getting user notification: {e}")
            return None