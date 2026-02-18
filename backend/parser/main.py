from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from src import api
from src.core import config, db
from src.core.logging import logger
from src.middlewares.exception import ExceptionMiddleware
from src.middlewares.time import TimeMiddleware
from src.services.auth import flows as auth_flows
from src.services.gamemode import flows as gamemode_flows
from src.services.hero import flows as hero_flows
from src.services.map import flows as map_flows
from starlette.requests import Request


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application... Online!")
    yield


async def not_found(request: Request, _: Exception):
    return ORJSONResponse(status_code=404, content={"detail": [{"msg": "Not Found"}]})


exception_handlers = {404: not_found}

app = FastAPI(
    title=config.app.project_name,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    debug=True if config.app.environment == "development" else False,
    root_path="/parser",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(TimeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.app.cors_origins if config.app.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH", "PUT"],
    allow_headers=["*"],
)

app.include_router(api.router)


@app.post("/seed", dependencies=[Depends(auth_flows.current_user)])
async def seed_database(session=Depends(db.get_async_session)):
    await gamemode_flows.initial_create(session)
    await hero_flows.initial_create(session)
    await map_flows.initial_create(session)
    return {"message": "Database seeded with gamemodes, heroes, and maps"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return ORJSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "msg": jsonable_encoder(
                        exc.errors(), exclude={"url", "type", "ctx"}
                    ),
                    "code": "unprocessable_entity",
                }
            ]
        },
    )
