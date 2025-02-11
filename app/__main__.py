# FastAPI packages
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# server
import uvicorn

# local imports
from app.routers.api_router import api_router
# from app.settings import settings
from app.exception import application_level_error

# for alembic migration
from .run_migration import run_migration

app = FastAPI(title="Template Backend.", version="0.1.0")
origins = ["http://localhost:5173"]

# Add application-level error handler middleware
app.middleware('http')(application_level_error)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Run migrations before starting the app
run_migration()

# Entry point for running the application
if __name__ == "__main__":
    uvicorn.run(
        app="app.__main__:app",
        # ssl_certfile=join(PATH, "cert", "server.crt"),
        # ssl_keyfile=join(PATH, "cert", "server.key"),
        loop="asyncio",
        host="0.0.0.0",
        port=8000,
        reload=True,
        env_file="../.env",
        # reload_dirs=["../"],
        # reload_includes=["../static", "../templates"],
    )
