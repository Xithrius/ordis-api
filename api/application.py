from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from api.lifetime import PrometheusMiddleware, lifespan, metrics
from api.routers import api_router
from api.settings import settings


def get_app() -> FastAPI:
    openapi_url = "/api/openapi.json" if settings.environment == "dev" else None

    app = FastAPI(
        title="ordis-api",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url=openapi_url,
        default_response_class=UJSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(PrometheusMiddleware, app_name="ordis-api")
    app.add_route("/metrics", metrics)

    app.include_router(router=api_router)

    return app
