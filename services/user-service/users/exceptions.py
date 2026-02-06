class DomainException(Exception):
    code = "DOMAIN_ERROR"
    message = "A domain error occurred."

    def __init__(self, message=None):
        if message:
            self.message = message
        super().__init__(self.message)


class UserAlreadyExists(DomainException):
    code = "USER_ALREADY_EXISTS"
    message = "A user with this email already exists."


class InvalidCredentials(DomainException):
    code = "INVALID_CREDENTIALS"
    message = "Invalid credentials."

class UserInactive(DomainException):
    code = "USER_INACTIVE"
    message = "User account is inactive."

