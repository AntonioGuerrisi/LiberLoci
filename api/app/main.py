import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import books, isbn, locations, portability, tags

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

app = FastAPI(title="LiberLoci", version="1.0.0", description="Self-hosted book inventory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(locations.router)
app.include_router(tags.router)
app.include_router(isbn.router)
app.include_router(portability.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
