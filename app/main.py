
from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference


from .database.session import create_db_tables

from .api.router import all_routers
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    print("Server started")
    await create_db_tables()
    yield
    print("Server stopped")


app = FastAPI(lifespan=lifespan_handler)


# Add cors here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(all_routers)


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )
