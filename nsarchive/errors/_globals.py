class ServerDownError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

# 4XX

class MissingParamError(Exception): # 400
    def __init__(self, *args):
        super().__init__(*args)

class InvalidParamError(Exception): # 400
    def __init__(self, *args):
        super().__init__(*args)

class AuthError(Exception): # 401
    def __init__(self, *args):
        super().__init__(*args)

class PermissionError(Exception): # 403
    def __init__(self, *args):
        super().__init__(*args)

class NotFoundError(Exception): # 404
    def __init__(self, *args):
        super().__init__(*args)

class ConflictError(Exception): # 409
    def __init__(self, *args):
        super().__init__(*args)