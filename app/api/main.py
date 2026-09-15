from fastapi import FastAPI
from app.api.indices import router

app = FastAPI()
app.include_router(router)

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}