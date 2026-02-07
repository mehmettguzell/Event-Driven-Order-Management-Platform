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


class ProductNotFound(DomainException):
    code = "PRODUCT_NOT_FOUND"
    message = "Product not found."
    status_code = 404


class ProductAlreadyExists(DomainException):
    code = "PRODUCT_ALREADY_EXISTS"
    message = "A product with this SKU already exists."
    status_code = 409


class InvalidPrice(DomainException):
    code = "INVALID_PRICE"
    message = "Price must be greater than zero."
    status_code = 400


class InvalidSKU(DomainException):
    code = "INVALID_SKU"
    message = "Invalid SKU format."
    status_code = 400


class InvalidToken(DomainException):
    code = "INVALID_TOKEN"
    message = "Token is invalid or expired."
    status_code = 401