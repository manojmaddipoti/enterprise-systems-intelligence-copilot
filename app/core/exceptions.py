from fastapi import HTTPException


def forbidden(message: str = "Not authorized") -> HTTPException:
    return HTTPException(status_code=403, detail=message)


def not_found(message: str = "Not found") -> HTTPException:
    return HTTPException(status_code=404, detail=message)
