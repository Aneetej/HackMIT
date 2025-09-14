#!/usr/bin/env python3
"""
Simple script to run the Student Agents API server
"""
import uvicorn
from studentagents.api import app

if __name__ == "__main__":
    print("🚀 Starting Student Agents API server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/api/health")
    print("\n🎯 Available endpoints:")
    print("  POST /api/chat/message - Send message to AI tutor")
    print("  GET  /api/chat/session/{id} - Get chat session")
    print("  POST /api/chat/session - Create new chat session")
    print("  GET  /api/student/{id}/profile - Get student profile")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
