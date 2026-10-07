from fastapi import FastAPI
from .api.document import router

app = FastAPI()

app.include_router(router)
