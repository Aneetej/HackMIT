from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from studentagents.view import respond_to_user_message

app = FastAPI(title="Student Agents API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessageRequest(BaseModel):
    chat_session_id: str
    student_id: str
    user_message: str
    class_id: str

class ChatMessageResponse(BaseModel):
    response: str
    chat_history: List[Dict]
    student_context: Optional[Dict] = None
    error: Optional[str] = None

@app.post("/api/chat/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Process a user message through AI agents and return response with chat history
    """
    try:
        result = respond_to_user_message(
            chat_session_id=request.chat_session_id,
            student_id=request.student_id,
            user_message=request.user_message,
            class_id=request.class_id
        )
        
        return ChatMessageResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "student-agents-api"}

@app.get("/api/chat/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session details and history"""
    try:
        from studentagents.prisma_client import PrismaClient
        from studentagents.view import run_async
        
        prisma_client = PrismaClient()
        connected = run_async(prisma_client.connect())
        
        if not connected:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        chat_session = run_async(prisma_client.get_chat_session_with_messages(session_id))
        run_async(prisma_client.disconnect())
        
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Format chat history
        chat_history = []
        if chat_session.get('messages'):
            chat_history = [
                {
                    "sender": msg["sender"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"]
                }
                for msg in sorted(chat_session['messages'], key=lambda x: x['timestamp'])
            ]
        
        return {
            "session_id": session_id,
            "topic": chat_session.get('topic', 'mathematics'),
            "chat_history": chat_history,
            "created_at": chat_session.get('created_at'),
            "updated_at": chat_session.get('updated_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get chat session: {str(e)}"
        )

class CreateSessionRequest(BaseModel):
    student_id: str
    class_id: str
    topic: Optional[str] = "mathematics"

@app.post("/api/chat/session")
async def create_chat_session(request: CreateSessionRequest):
    """Create a new chat session"""
    try:
        from studentagents.prisma_client import PrismaClient
        from studentagents.view import run_async
        
        prisma_client = PrismaClient()
        connected = run_async(prisma_client.connect())
        
        if not connected:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        # Create new chat session
        session = run_async(prisma_client.create_chat_session(
            student_id=request.student_id,
            class_id=request.class_id,
            topic=request.topic
        ))
        
        run_async(prisma_client.disconnect())
        
        return {
            "session_id": session["id"],
            "student_id": request.student_id,
            "class_id": request.class_id,
            "topic": request.topic,
            "created_at": session.get("created_at")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat session: {str(e)}"
        )

@app.get("/api/student/{student_id}/profile")
async def get_student_profile(student_id: str, class_id: str):
    """Get student profile and learning context"""
    try:
        from studentagents.prisma_client import PrismaClient
        from studentagents.view import run_async, map_student_data_to_context
        
        prisma_client = PrismaClient()
        connected = run_async(prisma_client.connect())
        
        if not connected:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        student_data = run_async(prisma_client.get_student_by_id_and_class(student_id, class_id))
        run_async(prisma_client.disconnect())
        
        if not student_data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Map to context format
        student_context = map_student_data_to_context(student_data)
        
        return {
            "student_id": student_id,
            "name": student_context["student_name"],
            "grade": student_context["grade"],
            "learning_style": student_context["learning_style"],
            "subject_focus": student_context["subject_focus"],
            "concepts_mastered": student_context["concepts_mastered"],
            "improvement_areas": student_context["improvement_areas"],
            "class_context": {
                "class_name": student_context["class_name"],
                "teacher_name": student_context["teacher_name"],
                "teaching_style": student_context["teaching_style"]
            },
            "statistics": {
                "total_sessions": student_context["total_sessions"],
                "total_messages": student_context["total_messages"],
                "average_engagement": student_context["average_engagement"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get student profile: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
