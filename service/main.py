# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routers import ai_router, crawler_router

app = FastAPI(
    title="Zameendaar - Property History Tracker",
    description="FastAPI service for AI-related operations and web crawling",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_router.router, prefix="/ai", tags=["ai"])
app.include_router(crawler_router.router, prefix="/crawler", tags=["crawler"])

@app.get("/")
async def root():
    return {"message": "AI & Web Crawling Service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)