# Database dependencies and common response helpers
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.engine import get_db
from typing import Any, Dict

def success_response(data: Any = None, message: str = "Success", status_code: int = status.HTTP_200_OK) -> JSONResponse:
    """Helper to create a standardized success response"""
    response_data: Dict[str, Any] = {"status": "success", "message": message}
    if data is not None:
        response_data["data"] = data
    return JSONResponse(content=response_data, status_code=status_code)

def error_response(message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Any = None) -> JSONResponse:
    """Helper to create a standardized error response"""
    response_data: Dict[str, Any] = {
        "status": "error",
        "message": message
    }
    if details is not None:
        response_data["details"] = details
    return JSONResponse(content=response_data, status_code=status_code)

def not_found_response(resource: str = "Resource") -> HTTPException:
    """Helper to create a 404 not found exception"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )

def validation_error_response(message: str, details: Any = None) -> HTTPException:
    """Helper to create a 422 validation error exception"""
    detail = {"message": message}
    if details:
        detail["details"] = details
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail
    )
