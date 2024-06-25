from flask import abort
from models.User import User
from models.Person import Person

def verify_user(userId):               
    user = User.get_user_by_id_model(userId)
    if not user:
        abort(400, {"message": "User not exist"})
    return user

def verify_email_registered(email):          
    user = User.get_user_by_email_model(email)
    if user:
        abort(400, {"message": "Email is not available"})
    return

def verify_username_registered(username):
    user = User.get_user_by_username_model(username)
    if user:
        abort(401, {"message": "Username is not available"})
    return

def verify_username(username):
    if ' ' in username:
        abort(400, {"message": "Username cannot contain spaces"})

def verify_person(personId, username):
    person = Person.get_person_by_id_model(personId)
    person2 = Person.get_person_by_username_model(username)
    if person:
        return True
    if person2:
        return True
    return False