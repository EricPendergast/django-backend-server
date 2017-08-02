from verifier import Verifier
from eledata.util import InvalidInputError



class CreateUserVerifier(Verifier):
    def stage0(self, request_data):
        self.ver_dict(request_data, required={"username","password","group"})
        
    stages = [stage0,]

class LoginVerifier(Verifier):
    def stage0(self, request_data):
        self.ver_dict(request_data, required={"username", "password"})
    
    stages = [stage0,]

class ChangePasswordVerifier(Verifier):
    def stage0(self, request_data, user):
        self.ver_dict(request_data, required={"username", "password", "new_password"})
        if request_data['username'] != user.username:
            raise InvalidInputError("Incorrect username. Make sure you are logged into your own account.")
        
        if not user.check_password(request_data["password"]):
            raise InvalidInputError("Incorrect password")
    
    stages = [stage0,]
