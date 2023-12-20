import base64
import contextlib

import databases
import jwt
import pyotp
from starlette.applications import Starlette
from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      AuthenticationError, SimpleUser,
                                      requires)
from starlette.background import BackgroundTask
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.routing import Mount, Route

import settings
from models import metadata, user
from utils import OrjsonResponse, send_mail

database = databases.Database(settings.DATABASE_URL)
tables = {}


async def detail(request):
    return OrjsonResponse({"hello": "world"})


async def list(request):
    return OrjsonResponse({"hello": "world"})


async def add(request):
    return OrjsonResponse({"hello": "world"})


async def update(request):
    return OrjsonResponse({"hello": "world"})


async def delete(request):
    return OrjsonResponse({"hello": "world"})


@requires("authenticated")
async def handler(request):
    path = request.url.path.split("/")[-1]
    table = tables[path]
    query = table.select()
    results = await database.fetch_all(query)
    return OrjsonResponse([dict(row) for row in results])


model_routes = []
for table in metadata.tables.values():
    model_routes.append(Route(f"/{table.name.__str__()}", endpoint=handler))
    tables[table.name.__str__()] = table


def send_otp_email(to_address, otp_code):
    """."""
    content = f"{otp_code}"
    send_mail("Finacial View verify code", content, to=[to_address])


async def login_otp(request):
    req = await request.json()
    email = req["email"]
    b32str = base64.b32encode(bytearray(email, "ascii")).decode("utf-8")
    totp = pyotp.TOTP(b32str, interval=settings.EMAIL_OTP_INTERVAL)
    if "otp_code" not in req:
        otp_code = totp.now()
        task = BackgroundTask(send_otp_email, to_address=email, otp_code=otp_code)
        message = {"detail": "check email", "interval": settings.EMAIL_OTP_INTERVAL}
        return OrjsonResponse(message, background=task)
    else:
        if not totp.verify(req["otp_code"]):
            raise HTTPException(status_code=401)
        value = {"email": email}
        query = "SELECT email FROM auth.user WHERE email = :email"
        result = await database.fetch_one(query=query, values=value)
        if not result:
            query = user.insert()
            await database.execute(query=query, values=value)
        value["token"] = jwt.encode(value, str(settings.SECRET_KEY), algorithm="HS256")
        return OrjsonResponse(value)


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            print(credentials)
            if scheme.lower() != "basic":
                return
        except Exception as exc:
            print(exc.with_traceback)
            raise AuthenticationError("Invalid basic auth credentials")

        decoded = jwt.decode(credentials, str(settings.SECRET_KEY), algorithms="HS256")
        username = decoded["email"]
        return AuthCredentials(["authenticated"]), SimpleUser(username)


routes = [
    Mount("/tables", routes=model_routes),
    Mount("/auth", routes=[Route("/login-otp/", methods=["POST"], endpoint=login_otp)]),
]

middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
    ),
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend()),
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
