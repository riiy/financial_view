import contextlib
import base64

import databases
import pyotp
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.exceptions import HTTPException
from starlette.requests import Request

import settings
from models import metadata, user
from utils import OrjsonResponse


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


async def login_otp(request):
    req = await request.json()
    email = req["email"]
    b32str = base64.b32encode(bytearray(email, "ascii")).decode("utf-8")
    totp = pyotp.TOTP(b32str, interval=30)
    if "otp_code" not in req:
        req["otp_code"] = totp.now()
    else:
        authenticated = totp.verify(req["otp_code"])
        if not authenticated:
            raise HTTPException(status_code=401)
        value = {"email": email}
        query = "SELECT email FROM auth.user WHERE email = :email"
        result = await database.fetch_one(query=query, values=value)
        if not result:
            query = user.insert()
            await database.execute(query=query, values=value)
    return OrjsonResponse(req)


routes = [
    Mount("/tables", routes=model_routes),
    Mount("/auth", routes=[Route("/login-otp/", methods=["POST"], endpoint=login_otp)]),
]

middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
    )
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
