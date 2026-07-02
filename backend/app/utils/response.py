from typing import Any


def success_response(data: Any, message: str = "OK") -> dict:
    return {"success": True, "message": message, "data": data}


def error_response(message: str, error_code: str) -> dict:
    return {"success": False, "message": message, "error_code": error_code}
