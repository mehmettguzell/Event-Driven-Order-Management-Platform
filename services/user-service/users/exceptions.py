class DomainException(Exception):
    code = "DOMAIN_ERROR"
    message = "A domain error occurred."
    status_code = 400

    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExists(DomainException):
    code = "USER_ALREADY_EXISTS"
    message = "A user with this email already exists."
    status_code = 409


class InvalidCredentials(DomainException):
    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password."
    status_code = 401


class UserInactive(DomainException):
    code = "USER_INACTIVE"
    message = "User account is inactive. Please contact support."
    status_code = 403


class InvalidToken(DomainException):
    code = "INVALID_TOKEN"
    message = "Token is invalid or expired."
    status_code = 401


class TokenBlacklisted(DomainException):
    code = "TOKEN_BLACKLISTED"
    message = "This token has been blacklisted."
    status_code = 401


class WeakPassword(DomainException):
    code = "WEAK_PASSWORD"
    message = "Password does not meet security requirements."
    status_code = 400
