import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import config

app = FastAPI(title="My FastAPI App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins
    allow_credentials=False,  # MUST be False when using "*"
    allow_methods=["*"],      # allow all HTTP methods
    allow_headers=["*"],      # allow all headers
)

app.include_router(api_router, prefix="/digidoc/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host=config["HOST"], port=8000, reload=config["IS_DEV"])