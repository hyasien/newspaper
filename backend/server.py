from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

# Import routes
from api.news_routes import router as news_router
from api.lebanon_routes import router as lebanon_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Breaking News API...")
    yield
    # Shutdown
    logger.info("Shutting down Breaking News API...")

# Create the main app
app = FastAPI(
    title="Breaking News & Lebanon Headlines API",
    description="API للأخبار العاجلة وعناوين الصحف اللبنانية",
    version="1.0.0",
    lifespan=lifespan
)

# Create API router
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Breaking News & Lebanon Headlines API is running", "status": "healthy"}

# Include news routes
api_router.include_router(news_router)
api_router.include_router(lebanon_router)

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)