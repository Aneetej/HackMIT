from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
# from studentagents.view import respond_to_user_message
from typing import Dict, List, Optional
from crewai import Task, Crew, Process
from studentagents.crew import Studentagents
from studentagents.prisma_client import PrismaClient
from studentagents.database_utils import (
    run_async, 
    map_student_data_to_context, 
    create_default_student_context
)

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
        print('start')
        
        result = await respond_to_user_message_async(
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

async def respond_to_user_message_async(chat_session_id: str, student_id: str, user_message: str, class_id: str) -> Dict:
    """
    Process user message through AI agents and return response with chat history (async version)
    """
    try:
        print('a)') 
        # Initialize Prisma client
        prisma_client = PrismaClient()
        print('b)')
        
        # Connect to database (now properly async)
        try:
            connected = await prisma_client.connect()
            print('c) connected:', connected)
        except Exception as connect_error:
            print('Database connection error:', connect_error)
            return {
                "response": f"I understand you're asking about '{user_message}'. I'm having some technical difficulties right now, but I'm here to help with your math questions!",
                "chat_history": [],
                "student_context": None,
                "error": f"Database connection failed: {str(connect_error)}"
            }
        
        if not connected:
            return {
                "response": f"I understand you're asking about '{user_message}'. I'm having some technical difficulties right now, but I'm here to help with your math questions!",
                "chat_history": [],
                "student_context": None,
                "error": "Database connection failed"
            }
        
        # Get student data and chat session (now async)
        student_data, chat_session, chat_history = await get_session_data_async(
            prisma_client, student_id, class_id, chat_session_id, user_message
        )
        print('d)')
        
        if isinstance(student_data, dict) and "error" in student_data:
            return student_data
        
        # Map student data to agent context
        student_context = map_student_data_to_context(student_data)
        
        # Create personalized agent crew
        student_crew = Studentagents(student_context=student_context)
        
        # Process message through agents
        try:
            agent_response = await process_message_with_crew_async(
                user_message, chat_history, student_crew, chat_session.get('topic', 'mathematics')
            )
        except Exception as agent_error:
            print(f"Agent processing error: {agent_error}")
            # Fallback to a helpful response if agent processing fails
            agent_response = f"I understand you're asking about '{user_message}'. Let me help you with that math concept. Can you provide more details about what specifically you'd like to learn?"
        
        # Save messages and return response
        return await save_and_return_response_async(
            prisma_client, chat_session_id, user_message, agent_response, 
            chat_history, student_context
        )
        
    except Exception as e:
        print(f"Error in respond_to_user_message_async: {e}")
        return {
            "response": f"I understand you're asking about '{user_message}'. I'm experiencing some technical difficulties, but I'm here to help with your math questions!",
            "chat_history": [],
            "student_context": None,
            "error": f"Processing failed: {str(e)}"
        }

async def get_session_data_async(prisma_client, student_id: str, class_id: str, chat_session_id: str, user_message: str):
    """Get student data and chat session (async version)"""
    try:
        # Get student data with class context
        student_data = await prisma_client.get_student_by_id_and_class(student_id, class_id)
        if not student_data:
            return {
                "error": "Student not found",
                "response": "Student profile not found. Please check your credentials.",
                "chat_history": []
            }, None, None
        
        # Get chat session with full message history
        chat_session = await prisma_client.get_chat_session_with_messages(chat_session_id)
        if not chat_session:
            return {
                "error": "Chat session not found", 
                "response": "Chat session not found. Please start a new session.",
                "chat_history": []
            }, None, None
        
        # Extract chat history in chronological order
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
        
        # Add current user message to history
        chat_history.append({
            "sender": "student",
            "content": user_message,
            "timestamp": None
        })
        
        return student_data, chat_session, chat_history
    except Exception as e:
        print(f"Error in get_session_data_async: {e}")
        return {
            "error": f"Data retrieval failed: {str(e)}",
            "response": "I encountered an error retrieving your data. Please try again.",
            "chat_history": []
        }, None, None

async def process_message_with_crew_async(user_message: str, chat_history: List[Dict], student_crew: Studentagents, topic: str) -> str:
    """Process message using CrewAI agents"""
    try:
        print ('a)')
        # Get student context from the crew
        student_context = student_crew.student_context
        
        # Step 1: Guideline Check
        guideline_agent = student_crew.guidelineAgent()
        guideline_task = student_crew.guidelineTask()
        
        guideline_crew = Crew(
            agents=[guideline_agent],
            tasks=[guideline_task],
            process=Process.sequential,
            verbose=False
        )
        print ('b')
        # Step 2: Get Relevance Examples
        relevance_agent = student_crew.relevanceAgent()
        relevance_task = student_crew.relevanceTask()
        
        relevance_task.description = f"""
        Find real-world examples for: "{user_message}" in the context of {topic}
        {relevance_task.description.format(
            topic=topic,
            learning_style=student_context.get('learning_style', 'visual'),
            student_name=student_context.get('student_name', 'Student'),
            improvement_areas=student_context.get('improvement_areas', 'word problems'),
            grade=student_context.get('grade', '10')
        )}
        """
        print ('c)')
        relevance_examples = ""
        try:
            relevance_crew = Crew(
                agents=[relevance_agent],
                tasks=[relevance_task],
                process=Process.sequential,
                verbose=False
            )
            
            relevance_result = relevance_crew.kickoff()
            relevance_examples = str(relevance_result)
        except Exception:
            relevance_examples = "No additional examples found at this time."
        print ('d)')
        # Step 3: Generate Tutor Response
        tutor_agent = student_crew.studentAgent()
        response_task = student_crew.studentTask()
        
        # Format conversation history for context
        conversation_context = "\n".join([
            f"{msg['sender']}: {msg['content']}" 
            for msg in chat_history[-10:]
        ])
        print ('e)')
        response_task.description = f"""
        Respond to the student's question or comment: "{user_message}"
        
        Context from previous conversation:
        {conversation_context}
        
        Real-world examples to incorporate:
        {relevance_examples}
        
        {response_task.description.format(
            topic=topic,
            student_name=student_context.get('student_name', 'Student'),
            learning_style=student_context.get('learning_style', 'visual'),
            concepts_mastered=student_context.get('concepts_mastered', 'basic concepts'),
            improvement_areas=student_context.get('improvement_areas', 'word problems'),
            grade=student_context.get('grade', '10'),
            teacher_name=student_context.get('teacher_name', 'Teacher'),
            teaching_style=student_context.get('teaching_style', 'interactive'),
            preferred_content=student_context.get('preferred_content', 'interactive'),
            total_sessions=student_context.get('total_sessions', 1),
            subject_focus=student_context.get('subject_focus', 'algebra')
        )}
        
        Make sure to incorporate the real-world examples naturally into your response to help the student understand why this matters.
        """
        print ('ea)')
        # Create crew for response generation
        response_crew = Crew(
            agents=[tutor_agent],
            tasks=[response_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = response_crew.kickoff()
        return str(result)
        
    except Exception as e:
        print(f"Error in process_message_with_crew_async: {e}")
        return f"I encountered an error while processing your question about '{user_message}'. Let me try to help you anyway - could you rephrase your question or provide more context?"

async def save_and_return_response_async(prisma_client, chat_session_id: str, user_message: str, 
                           agent_response: str, chat_history: List[Dict], student_context: Dict) -> Dict:
    """Save messages to database and return formatted response"""
    try:
        # Save user message to database
        await prisma_client.add_chat_message(
            session_id=chat_session_id,
            sender_type="student",
            content=user_message
        )
        
        # Save agent response to database  
        await prisma_client.add_chat_message(
            session_id=chat_session_id,
            sender_type="agent",
            content=agent_response,
            agent_type="student_agent"
        )
        
        # Add agent response to chat history
        chat_history.append({
            "sender": "agent",
            "content": agent_response,
            "timestamp": None
        })
        
        return {
            "response": agent_response,
            "chat_history": chat_history,
            "student_context": {
                "name": student_context.get("student_name", "Student"),
                "learning_style": student_context.get("learning_style", "mixed"),
                "grade": student_context.get("grade", "10")
            },
            "error": None
        }
        
    except Exception as e:
        print(f"Error saving messages: {e}")
        return {
            "response": agent_response,
            "chat_history": chat_history,
            "student_context": {
                "name": student_context.get("student_name", "Student"),
                "learning_style": student_context.get("learning_style", "mixed"),
                "grade": student_context.get("grade", "10")
            },
            "error": f"Database save failed: {str(e)}"
        }
    finally:
        # Disconnect from database
        await prisma_client.disconnect()

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
            "name": student_context.get("student_name", "Student"),
            "grade": student_context.get("grade", "10"),
            "learning_style": student_context.get("learning_style", "mixed"),
            "subject_focus": student_context.get("subject_focus", "algebra"),
            "concepts_mastered": student_context.get("concepts_mastered", "basic concepts"),
            "improvement_areas": student_context.get("improvement_areas", "word problems"),
            "class_context": {
                "name": student_context.get("class_name", "Demo Class"),
                "teacher": student_context.get("teacher_name", "Teacher"),
                "teaching_style": student_context.get("teaching_style", "interactive")
            },
            "learning_metrics": {
                "total_sessions": student_context.get("total_sessions", 0),
                "total_messages": student_context.get("total_messages", 0),
                "engagement_score": student_context.get("average_engagement", 75)
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
    uvicorn.run(app, host="localhost", port=8000)
