import logging
from functools import wraps

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.context import permissions_var


class DecoratorUtil:
    @staticmethod
    def require_access(permission: str):
        """
        Restrict endpoint access to users holding the given permission.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Fetch the user's permissions stored in request context
                user_permissions = permissions_var.get() or []

                # Allow all actions for super admins
                if "*" in user_permissions:
                    return func(*args, **kwargs)

                # Support module-level wildcard access (e.g., "tickets.*")
                component = permission.split(":")[0]
                wildcard = f"{component}:*"

                # Block if required permission is missing
                if permission not in user_permissions and wildcard not in user_permissions:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "success": False,
                            "status": 403,
                            "message": f"Missing required permission: {permission}",
                            "error": {
                                "type": "missing_permission",
                                "metadata": {
                                    "required_permission": permission,
                                    "user_permissions": user_permissions,
                                },
                            },
                        },
                    )

                # Execute endpoint if authorized
                return func(*args, **kwargs)

            return wrapper

        return decorator


# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Define logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request details
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = request.url.path

        logger.info(f"Request: {method} {url} from {client_ip}")

        # Process the request
        response = await call_next(request)

        # Log response details
        status_code = response.status_code
        logger.info(f"Response: {method} {url} returned {status_code} to {client_ip}")

        return response
