from fastapi import FastAPI
from app.api.indices import router

app = FastAPI()
app.include_router(router)
