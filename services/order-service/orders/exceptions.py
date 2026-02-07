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


class OrderNotFound(DomainException):
    code = "ORDER_NOT_FOUND"
    message = "Order not found."
    status_code = 404