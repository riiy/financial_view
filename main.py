import contextlib
import random
from datetime import datetime, timedelta

import databases
import jwt
from loguru import logger
from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    requires,
)
from starlette.background import BackgroundTask
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.routing import Mount, Route
from sqlalchemy.dialects.postgresql import insert

import settings
from models import metadata, user
from utils import OrjsonResponse, send_mail

database = databases.Database(settings.DATABASE_URL)
tables = {}


class Api(HTTPEndpoint):
    async def get(self, request):
        path = request.url.path.split("/")[-1]
        table = tables[path]
        async with database.transaction():
            if request.user.is_authenticated:
                email = request.user.display_name
                logger.info(email)
                await database.execute(f"set role {settings.AUTH_ROLE};")
                await database.execute(
                    f"select set_config('user.jwt.claims.email','{email}',true);"
                )
            query = table.select()
            results = await database.fetch_all(query)
        return OrjsonResponse([dict(row) for row in results])

    async def post(self, request):
        return OrjsonResponse({"hello": "post"})

    async def put(self, request):
        return OrjsonResponse({"hello": "put"})

    async def delete(self, request):
        return OrjsonResponse({"hello": "delete"})


model_routes = []
for table in metadata.tables.values():
    if table.schema.__str__() in ["auth"]:
        continue

    model_routes.append(Route(f"/{table.name.__str__()}", endpoint=Api))
    tables[table.name.__str__()] = table


class Login(HTTPEndpoint):
    def _send_verify_code_task(self, email, verify_code):
        """."""
        send_mail(
            subject="verify code",
            content=verify_code,
            to=[email],
            sender="Finacial View",
        )

    async def post(self, request):
        req = await request.json()
        email = req["email"]
        resp = {"email": email}
        values = {
            "email": email,
            "interval": datetime.now() - timedelta(seconds=int(settings.EMAIL_INTERVAL)),
        }
        query = "SELECT verify_code FROM auth.user WHERE email = :email and update_time > :interval;"
        result = await database.fetch_one(query=query, values=values)
        if not result or result.verify_code != req["captcha"]:
            raise HTTPException(status_code=401)
        resp["token"] = jwt.encode(resp, str(settings.SECRET_KEY), algorithm="HS256")
        resp["type"] = "email"
        resp["currentAuthority"] = "user"
        return OrjsonResponse(resp)

    async def get(self, request):
        email = request.query_params.get("email")
        if not email:
            raise HTTPException(status_code=401)
        verify_code = str(random.randint(1000, 9999))
        insert_stmt = insert(user).values(email=email, verify_code=verify_code)
        do_update_stmt = insert_stmt.on_conflict_do_update(
            constraint="user_pkey", set_=dict(verify_code=verify_code)
        )
        await database.execute(do_update_stmt)
        task = BackgroundTask(
            self._send_verify_code_task, email=email, verify_code=verify_code
        )
        message = {"detail": "check email", "interval": settings.EMAIL_INTERVAL}
        return OrjsonResponse(message, background=task)


login_route = [
    Route("/login/account", endpoint=Login),
    Route("/login/captcha", methods=["GET"], endpoint=Login),
]

# routes
routes = [
    Mount("/api", routes=model_routes + login_route),
]


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "bearer":
                return
        except Exception as exc:
            logger.info(exc.with_traceback)
            raise AuthenticationError("Invalid basic auth credentials")

        decoded = jwt.decode(credentials, str(settings.SECRET_KEY), algorithms="HS256")
        email = decoded["email"]
        return AuthCredentials(["authenticated"]), SimpleUser(email)


middleware = [
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend()),
    Middleware(CORSMiddleware, allow_origins=["*"]),
]


@contextlib.asynccontextmanager
async def lifespan(app):
    await database.connect()
    yield
    await database.disconnect()


async def http_exception(request: Request, exc: HTTPException):
    return OrjsonResponse({"detail": exc.detail}, status_code=exc.status_code)


exception_handlers = {HTTPException: http_exception}


app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    middleware=middleware,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)
