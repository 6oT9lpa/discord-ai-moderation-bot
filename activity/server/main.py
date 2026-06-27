from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from activity.server.config import activity_server_config
from activity.server.dependencies import initialize_activity_dependencies, shutdown_activity_dependencies
from activity.server.middleware import configure_activity_middleware
from activity.server.routers import include_activity_routers


def create_app() -> FastAPI:
    app = FastAPI(title="Omnibot Activity API")
    configure_activity_middleware(app)

    @app.on_event("startup")
    async def startup() -> None:
        await initialize_activity_dependencies()

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await shutdown_activity_dependencies()

    include_activity_routers(app)
    mount_activity_client(app)
    return app


def mount_activity_client(app: FastAPI) -> None:
    client_dist = activity_server_config.client_dist
    if client_dist.exists():
        app.mount("/assets", StaticFiles(directory=client_dist / "assets"), name="activity-assets")


app = create_app()


@app.get("/{path:path}")
async def serve_activity(path: str) -> FileResponse:
    if path.startswith("api/"):
        raise HTTPException(status_code=404)

    client_dist = activity_server_config.client_dist
    requested = client_dist / path
    if requested.is_file():
        return FileResponse(requested)
    return FileResponse(client_dist / "index.html")
