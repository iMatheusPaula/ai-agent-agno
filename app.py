from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from middlewares.auth_middleware import api_key_middleware
from modules.agents.router import agents_router

app = FastAPI()

app.middleware("http")(api_key_middleware)

app.include_router(agents_router, tags=["agents"], prefix="/agents")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Root route to serve the test page
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")
