from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import file, users
from app.utils.logging import configure_logging

# Configure logging
configure_logging()

app = FastAPI()

# CORS settings
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(file.router, tags=["File"])  
app.include_router(users.router, tags=["Users"])
