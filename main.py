import contextlib

import databases
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount


import settings
from tables import metadata

database = databases.Database(settings.DATABASE_URL)
tables = {}
table_routes = []


@contextlib.asynccontextmanager
async def lifespan(app):
    await database.connect()
    yield
    await database.disconnect()


async def get(request):
    path = request.url.path.split('/')[-1]
    table = tables[path]
    query = table.select()
    results = await database.fetch_all(query)
    return JSONResponse([dict(row) for row in results])


async def detail(request):
    return JSONResponse({"hello": "world"})


async def post(request):
    return JSONResponse({"hello": "world"})


async def put(request):
    return JSONResponse({"hello": "world"})


async def delete(request):
    return JSONResponse({"hello": "world"})


for table in metadata.tables.values():
    table_routes.append(Route(f"/{table.name.__str__()}", endpoint=get))
    tables[table.name.__str__()] = table
routes = [Mount("/tables", routes=table_routes)]
middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
    )
]

app = Starlette(debug=settings.DEBUG, routes=routes, middleware=middleware, lifespan=lifespan)
