from verifier import Verifier



class CreateUserVerifier(Verifier):
    def stage0(self, request_data):
        self.ver_dict(request_data, required={"username","password","group"}, options={})
        
    stages = [stage0,]

class LoginVerifier(Verifier):
    def stage0(self, request_data):
        self.ver_dict(request_data, required={"username", "password"}, options={})
    
    stages = [stage0,]
