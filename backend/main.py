import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.endpoints import router as api_router

app = FastAPI(
    title="High-Performance Sports Telemetry & Biometrics Platform",
    description="Engine for multi-device smartwatch synchronization, HRV analysis, sleep architecture, and metabolic energy expenditure for elite athletes.",
    version="1.0.0"
)

# Enable CORS for development and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "High-Performance Sports Science Telemetry API is running",
        "docs_url": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
