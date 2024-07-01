from models.Person import Person
from models.User import User
from middleware.all_middleware import verify_person

def create_person_controller(personId, username):
    user = User.get_user_by_username_model(username)
    if not user:
        return {"message": "User does not exist"}, 400
    
    person_registered = verify_person(personId, username)
    if person_registered:
        return({"message": "Person already exists"}, 400)
    
    user_id = Person.create_user_model(personId, username)
    User.update_user_role(user.get("_id"), "person")
    return {"message": f"Person with id {personId} and user {username} created"}, 200