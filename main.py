import contextlib
import random
from datetime import datetime, timedelta
from typing import Dict
import httpx

import databases
import jwt
import sqlalchemy as sa
from loguru import logger
from sqlalchemy.dialects.postgresql import insert
from starlette.applications import Starlette
from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      AuthenticationError, SimpleUser)
from starlette.background import BackgroundTask
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.responses import Response

import settings
from models import metadata, users
from utils import OrjsonResponse, send_mail

database = databases.Database(settings.DATABASE_URL)

tables: Dict[str, sa.Table] = {}


class Api(HTTPEndpoint):
    """API."""

    async def get(self, request):
        """GET."""
        path = request.url.path.split("/")[-1]
        model = tables[path]
        async with database.transaction():
            await database.execute(f"set role {settings.AUTH_ROLE};")
            if request.user.is_authenticated:
                email = request.user.display_name
                await database.execute(
                    f"select set_config('user.jwt.claims.email','{email}',true);"
                )
            query = model.select()
            results = await database.fetch_all(query)
        return OrjsonResponse([dict(row) for row in results])

    async def post(self, request):
        """POST."""
        logger.info(request)
        return OrjsonResponse({"hello": "post"})

    async def put(self, request):
        """."""
        logger.info(request)
        return OrjsonResponse({"hello": "put"})

    async def delete(self, request):
        """."""
        logger.info(request)
        return OrjsonResponse({"hello": "delete"})


model_routes = []
for table in metadata.tables.values():
    if str(table.schema) in ["auth"]:
        continue
    model_routes.append(Route(f"/{str(table.name)}", endpoint=Api))
    tables[str(table.name)] = table


class Login(HTTPEndpoint):
    """LOGIN."""

    def _send_verify_code_task(self, email, verify_code):
        """."""
        send_mail(
            subject="verify code",
            content=verify_code,
            to=[email],
            sender="Finacial View",
        )

    async def post(self, request):
        """."""
        req = await request.json()
        email = req["email"]
        resp = {"email": email}
        values = {
            "email": email,
            "interval": datetime.now()
            - timedelta(seconds=int(settings.EMAIL_INTERVAL)),
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
        """."""
        email = request.query_params.get("email")
        if not email:
            raise HTTPException(status_code=401)
        verify_code = str(random.randint(1000, 9999))
        insert_stmt = insert(users).values(email=email, verify_code=verify_code)
        do_update_stmt = insert_stmt.on_conflict_do_update(
            constraint="user_pkey", set_={"verify_code": verify_code}
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


async def spot(request):
    """."""
    url = "http://82.push2.eastmoney.com/api/qt/clist/get"
    page = request.query_params.get('page', 1)
    if int(page) > 480:
        raise HTTPException(status_code=404)
    params = {
        "pn": f"{page}",
        "pz": "100",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
        "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
        "_": "1623833739532",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)

    return Response(resp.text, media_type='application/json')

async def test(request):
    message = {"detail": "test"}
    return OrjsonResponse(message)

proxy_route = [
    Route("/proxy/spot", endpoint=spot),
    Route("/proxy/test", endpoint=test),
]
# routes
routes = [
    Mount("/api", routes=model_routes + login_route + proxy_route),
]


class BasicAuthBackend(AuthenticationBackend):
    """AuthBackend."""

    async def authenticate(self, conn):
        """."""
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
    """."""
    await database.connect()
    yield
    await database.disconnect()


async def http_exception(request: Request, exc: HTTPException):
    """."""
    return OrjsonResponse({"detail": exc.detail}, status_code=exc.status_code)


exception_handlers = {HTTPException: http_exception}


app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    middleware=middleware,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)
