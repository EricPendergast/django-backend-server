from eledata.util import InvalidInputError

# The way verifiers work is that they contain a list of stages, where each
# stage verifies different things. Each stage is a function which takes as
# input the fields it will validate. In order for the verifier to be verified,
# (ie verifier.verified == True), all the stages must be run in the order
# specified in 'stages'. If, at any point, a stage encounters an invalid input,
# it should throw an exception. Keep in mind that if a stage throws an
# exception, the verifier will not move on to the next stage, so the caller
# will have to execute the same stage again until it validates.


# A convention note: For simplicity, in a single stage there should be no
# statements that depend on past statements in that same stage. For example,
# you should never have:
#
# def stage0(entity):
#     if entity is None:
#          raise Exception()
#     if entity.data is None:
#          raise Exception()
#
# 
# Instead, split it up:
#
# def stage0(entity):
#     if entity is None:
#          raise Exception()
#
# def stage1(entity_data):
#     if entity_data is None:
#          raise Exception()
#
#
# This improves readability for the caller

class Verifier(object):
    # The list of verifying functions, in order of the order they need to be
    # run in
    stages = []
    
    def __init__(self):
        self.next_stage = 0
        
    def verify(self, stage, *args, **kwargs):
        assert not self.verified, "This verifier is already verified"
        assert stage == self.next_stage
        
        self.stages[stage](self, *args, **kwargs)
        self.next_stage += 1
    
    @property
    def verified(self):
        return self.next_stage == len(self.stages)
    
    @staticmethod
    def ver_field(data, field, required, options):
        return not (field in options) or (data[field] in options[field])
    
    # Checks that 'data' contains all items in 'required' and that every key in
    # 'data' that is also in 'options' maps to one of the options given in
    # 'options'. If it fails, it throws a helpful error message. 
    @staticmethod
    def ver_dict(data, required=set(), options={}):
        # Verify 'data' has all the required fields
        for field in required:
            if not field in data:
                raise InvalidInputError("Missing field: %s" % field)
        # Verify that every field in 'data' follows the correct format
        for field in data:
            if not Verifier.ver_field(data, field, required, options):
                raise InvalidInputError("Invalid field entry: %s->%s" % (field, data[field]))
