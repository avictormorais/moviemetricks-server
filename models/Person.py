
from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database(os.getenv("MONGODB_DBNAME"))

class Person:
    @staticmethod
    def create_user_model(personId, username):
        try:
            users_collection = db.persons
            new_person = {
                "username": username,
                "personId": personId
            }
            result = users_collection.insert_one(new_person)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating Person: {e}")
            return None
        
    def get_person_by_id_model(personId):
      try:
        users_collection = db.persons
        person = users_collection.find_one({"personId": personId})
        return person
      except Exception as e:
        print(f"Error getting person by id: {e}")
        return None

    @staticmethod
    def get_person_by_username_model(username):
      try:
        users_collection = db.persons
        person = users_collection.find_one({"username": username})
        return person
      except Exception as e:
        print(f"Error getting person by username: {e}")
        return None