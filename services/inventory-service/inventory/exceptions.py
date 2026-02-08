from typing import Any, Optional


class InventoryAPIException(Exception):

    code: str = "ERROR"
    message: str = "An error occurred."
    status_code: int = 500
    details: Optional[dict[str, Any]] = None

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message or self.message)
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        if details is not None:
            self.details = details


class InventoryNotFoundError(InventoryAPIException):
    code = "NOT_FOUND"
    message = "Inventory not found for this product."
    status_code = 404


class InsufficientStockError(InventoryAPIException):
    code = "INSUFFICIENT_STOCK"
    message = "Insufficient stock for the requested product."
    status_code = 409
