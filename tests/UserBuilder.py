import bcrypt
import base64

class UserBuilder:
    
    def __init__(self):
        self.user = {
            "username": "",
            "email": "",
            "password": ""

        }
    @staticmethod
    def anUser():
        
        builder = UserBuilder()

        password = "Testando"

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10))
        hashed_password_base64 = base64.b64encode(hashed_password).decode()

        builder.user['username'] = "Teste1"
        builder.user['email'] = "qwertyu@email.com"
        builder.user['password'] = hashed_password_base64

        return builder
    
    def now(self):
        
        return self.user
        