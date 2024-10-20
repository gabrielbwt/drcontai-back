from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import status, pluggy

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router)
app.include_router(pluggy.router)
