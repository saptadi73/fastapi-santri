"""Standardized JSON response utilities."""

from typing import Any, Optional, Dict, List
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from fastapi.encoders import jsonable_encoder


class JSONResponse:
    """Standardized JSON response builder."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> FastAPIJSONResponse:
        """
        Return a success response.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata
            
        Returns:
            FastAPIJSONResponse with standardized format
        """
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            response["meta"] = meta
            
        return FastAPIJSONResponse(
            content=jsonable_encoder(response),
            status_code=status_code
        )

    @staticmethod
    def error(
        message: str = "Error occurred",
        status_code: int = 400,
        errors: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ) -> FastAPIJSONResponse:
        """
        Return an error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            errors: Detailed error information
            error_code: Application-specific error code
            
        Returns:
            FastAPIJSONResponse with standardized format
        """
        response = {
            "success": False,
            "message": message,
            "data": None
        }
        
        if errors:
            response["errors"] = errors
            
        if error_code:
            response["error_code"] = error_code
            
        return FastAPIJSONResponse(
            content=jsonable_encoder(response),
            status_code=status_code
        )

    @staticmethod
    def paginated(
        data: List[Any],
        page: int,
        per_page: int,
        total: int,
        message: str = "Success",
        status_code: int = 200
    ) -> FastAPIJSONResponse:
        """
        Return a paginated response.
        
        Args:
            data: List of items for current page
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message
            status_code: HTTP status code
            
        Returns:
            FastAPIJSONResponse with pagination metadata
        """
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        
        response = {
            "success": True,
            "message": message,
            "data": data,
            "meta": {
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        }
        
        return FastAPIJSONResponse(
            content=jsonable_encoder(response),
            status_code=status_code
        )


# Convenience functions
def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None
) -> FastAPIJSONResponse:
    """Shorthand for JSONResponse.success()."""
    return JSONResponse.success(data, message, status_code, meta)


def error_response(
    message: str = "Error occurred",
    status_code: int = 400,
    errors: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None
) -> FastAPIJSONResponse:
    """Shorthand for JSONResponse.error()."""
    return JSONResponse.error(message, status_code, errors, error_code)


def paginated_response(
    data: List[Any],
    page: int,
    per_page: int,
    total: int,
    message: str = "Success",
    status_code: int = 200
) -> FastAPIJSONResponse:
    """Shorthand for JSONResponse.paginated()."""
    return JSONResponse.paginated(data, page, per_page, total, message, status_code)
