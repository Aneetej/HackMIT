from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

# Import our agent system and database
from agents.agent_orchestrator import AgentOrchestrator
from database.connection import get_db_connection
from api.routes import student_router, teacher_router, analytics_router

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting MathEngageAI...")
    
    # Initialize database connection
    await get_db_connection()
    
    # Initialize agent orchestrator
    app.state.agent_orchestrator = AgentOrchestrator()
    await app.state.agent_orchestrator.initialize()
    
    print("✅ All systems initialized successfully!")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down MathEngageAI...")
    await app.state.agent_orchestrator.cleanup()
    print("✅ Shutdown complete!")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="MathEngageAI",
    description="Hierarchical AI Network for Mathematics Learning Engagement",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(student_router, prefix="/api/student", tags=["Student"])
app.include_router(teacher_router, prefix="/api/teacher", tags=["Teacher"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "MathEngageAI - Hierarchical AI Network for Mathematics Learning",
        "status": "active",
        "version": "1.0.0",
        "agents": {
            "teacher_agent": "monitoring",
            "student_agent": "ready",
            "guardrail_agent": "active",
            "aggregation_agent": "collecting",
            "takeaway_agent": "analyzing"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = await get_db_connection()
        
        return {
            "status": "healthy",
            "database": "connected" if db_status else "disconnected",
            "agents": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "localhost"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )
