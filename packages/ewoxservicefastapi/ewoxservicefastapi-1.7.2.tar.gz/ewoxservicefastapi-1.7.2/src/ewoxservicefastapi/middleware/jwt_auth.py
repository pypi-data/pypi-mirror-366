from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request, status
from ewoxcore.service.authorizer import Authorizer
from ewoxcore.service.interfaces.iauthorizer import IAuthorizer
from ewoxcore.service.service import get_service

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes if needed
        if request.url.path in ["/login", "/register"]:
            return await call_next(request)

        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing or invalid"},
            )

        token = auth_header.split(" ")[1]

        try:
            # payload = decode_jwt_token(token)
            # # Store user info in request.state if needed
            # request.state.user = payload
            authorizer:IAuthorizer = get_service(IAuthorizer)
            res:bool = authorizer.is_authorized(token)
            if (res == False):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        return await call_next(request)
