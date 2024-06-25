import os
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from models.User import User
from bson import ObjectId
from flask import Flask
import jwt

load_dotenv()
JWT_key= os.getenv("JWT_SECRET_KEY")

class TestUser(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['JWT_TOKEN_LOCATION'] = ['headers']
        self.app.config['JWT_HEADER_NAME'] = 'Authorization'
        self.app.config['JWT_HEADER_TYPE'] = 'Bearer'
        self.app.config['JWT_SECRET_KEY'] = JWT_key
        self.jwt = JWTManager(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('models.User.db.users')
    def test_create_user_model(self, mock_users_collection):
        mock_users_collection.insert_one.return_value.inserted_id = ObjectId("60d5f7e8f8d3fcd7c6dbb123")
        
        user_id = User.create_user_model("email@example.com", "username", "role", "hashed_password")
        
        self.assertEqual(user_id, "60d5f7e8f8d3fcd7c6dbb123")
        mock_users_collection.insert_one.assert_called_once_with({
            "username": "username",
            "email": "email@example.com",
            "role": "role",
            "password": "hashed_password",
            "watched": []
        })

    @patch('models.User.db.users')
    def test_get_user_by_username_model(self, mock_users_collection):
        mock_user = {"username": "username"}
        mock_users_collection.find_one.return_value = mock_user
        
        user = User.get_user_by_username_model("username")
        
        self.assertEqual(user, mock_user)
        mock_users_collection.find_one.assert_called_once_with({"username": "username"})
    
    @patch('models.User.db.users')
    def test_get_user_by_email_model(self, mock_users_collection):
        mock_user = {"email": "email@example.com"}
        mock_users_collection.find_one.return_value = mock_user
        
        user = User.get_user_by_email_model("email@example.com")
        
        self.assertEqual(user, mock_user)
        mock_users_collection.find_one.assert_called_once_with({"email": "email@example.com"})
    
    @patch('models.User.db.users')
    def test_get_user_by_id_model(self, mock_users_collection):
        mock_user = {"_id": ObjectId("60d5f7e8f8d3fcd7c6dbb123")}
        mock_users_collection.find_one.return_value = mock_user
        
        user = User.get_user_by_id_model("60d5f7e8f8d3fcd7c6dbb123")
        
        self.assertEqual(user, mock_user)
        mock_users_collection.find_one.assert_called_once_with({"_id": ObjectId("60d5f7e8f8d3fcd7c6dbb123")})
    
    @patch('models.User.db.users')
    def test_update_user(self, mock_users_collection):
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 1
        mock_users_collection.update_many.return_value = mock_update_result

        result = User.update_user("60d5f7e8f8d3fcd7c6dbb123", {"username": "new_username"})
        
        self.assertTrue(result)
        mock_users_collection.update_many.assert_called_once_with(
            {"_id": ObjectId("60d5f7e8f8d3fcd7c6dbb123")},
            {"$set": {"username": "new_username"}}
        )

    @patch('models.User.db.users')
    def test_delete_account_model(self, mock_users_collection):
        mock_users_collection.find_one_and_delete.return_value = {"_id": ObjectId("60d5f7e8f8d3fcd7c6dbb123")}
        
        result = User.delete_account_model("60d5f7e8f8d3fcd7c6dbb123")
        
        self.assertTrue(result)
        mock_users_collection.find_one_and_delete.assert_called_once_with({"_id": ObjectId("60d5f7e8f8d3fcd7c6dbb123")})
    
    @patch('models.User.MediaAPI.get_or_create_media')
    @patch('models.User.db.users')
    @patch('models.User.get_jwt_identity')
    def test_add_watched_list(self, mock_get_jwt_identity, mock_users_collection, mock_get_or_create_media):
        mock_get_jwt_identity.return_value = "60d5f7e8f8d3fcd7c6dbb123"
        mock_get_or_create_media.return_value = {
            "title": "Some Title",
            "poster_path": "some_path",
            "vote_average": 8,
            "release_date": "2020-01-01"
        }
        mock_users_collection.update_one.return_value.modified_count = 1
        
        result = User.add_watched_list("tmdb_id", "media_type", "api_key")
        
        self.assertTrue(result)
        mock_users_collection.update_one.assert_called_once_with(
            {"_id": ObjectId("60d5f7e8f8d3fcd7c6dbb123")},
            {"$addToSet": {
                "watched": {
                    "tmdb_id": "tmdb_id",
                    "media_type": "media_type",
                    "title": "Some Title",
                    "poster_path": "some_path",
                    "vote_average": 8,
                    "release_date": "2020-01-01"
                }
            }}
        )

    @patch('models.User.MediaAPI.get_or_create_media')
    @patch('models.User.db.users')
    @patch('models.User.get_jwt_identity')
    @patch('models.User.User.get_user_by_id_model')
    def test_delete_from_watched_list(self, mock_get_user_by_id_model, mock_get_jwt_identity, mock_users_collection, mock_get_or_create_media):
        mock_get_jwt_identity.return_value = "60d5f7e8f8d3fcd7c6dbb123"
        mock_get_user_by_id_model.return_value = True
        mock_get_or_create_media.return_value = True
        mock_users_collection.update_one.return_value.modified_count = 1

        token = jwt.encode({"sub": "60d5f7e8f8d3fcd7c6dbb123"}, self.app.config['JWT_SECRET_KEY'].encode(), algorithm="HS256")
        with self.app.test_request_context('/', headers={'Authorization': f'Bearer {token}'}):
            result = User.delete_from_watched_list("tmdb_id", "media_type", "api_key")
        
        self.assertTrue(result)
        mock_users_collection.update_one.assert_called_once_with(
            {"_id": ObjectId("60d5f7e8f8d3fcd7c6dbb123")},
            {"$pull": {"watched": {"tmdb_id": "tmdb_id", "media_type": "media_type"}}}
        )

if __name__ == '__main__':
    unittest.main()