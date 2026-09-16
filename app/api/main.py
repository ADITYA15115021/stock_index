from fastapi import FastAPI
from app.api.indices import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://<frontend-render-url>.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}