from typing import Dict, List, Optional
from crewai import Task, Crew, Process
from studentagents.crew import Studentagents
from studentagents.prisma_client import PrismaClient
from studentagents.database_utils import (
    run_async, 
    map_student_data_to_context, 
    create_default_student_context
)

def respond_to_user_message(chat_session_id: str, student_id: str, user_message: str, class_id: str) -> Dict:
    """
    Process user message through AI agents and return response with chat history
    """
    try:
        # Initialize Prisma client
        prisma_client = PrismaClient()
        
        # Connect to database
        connected = run_async(prisma_client.connect())
        if not connected:
            return {
                "error": "Database connection failed",
                "response": "I'm having trouble connecting to the database. Please try again.",
                "chat_history": []
            }
        
        # Get student data and chat session
        student_data, chat_session, chat_history = get_session_data(
            prisma_client, student_id, class_id, chat_session_id, user_message
        )
        
        if isinstance(student_data, dict) and "error" in student_data:
            return student_data
        
        # Map student data to agent context
        student_context = map_student_data_to_context(student_data)
        
        # Create personalized agent crew
        student_crew = Studentagents(student_context=student_context)
        
        # Process message through agents (reusing interactive_main logic)
        agent_response = process_message_with_crew(
            user_message, chat_history, student_crew, chat_session.get('topic', 'mathematics')
        )
        
        # Save messages and return response
        return save_and_return_response(
            prisma_client, chat_session_id, user_message, agent_response, 
            chat_history, student_context
        )
        
    except Exception as e:
        return {
            "error": f"Processing failed: {str(e)}",
            "response": "I encountered an error processing your message. Please try again.",
            "chat_history": []
        }

def get_session_data(prisma_client, student_id: str, class_id: str, chat_session_id: str, user_message: str):
    """Get student data and chat session, reusing interactive_main logic"""
    # Get student data with class context
    student_data = run_async(prisma_client.get_student_by_id_and_class(student_id, class_id))
    if not student_data:
        return {
            "error": "Student not found",
            "response": "Student profile not found. Please check your credentials.",
            "chat_history": []
        }, None, None
    
    # Get chat session with full message history
    chat_session = run_async(prisma_client.get_chat_session_with_messages(chat_session_id))
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

def process_message_with_crew(user_message: str, chat_history: List[Dict], student_crew: Studentagents, topic: str) -> str:
    """Process message using the same logic as interactive_main.py"""
    try:
        # Step 1: Guideline Check (reusing interactive_main pattern)
        guideline_agent = student_crew.guidelineAgent()
        guideline_task = student_crew.guidelineTask()
        
        guideline_crew = Crew(
            agents=[guideline_agent],
            tasks=[guideline_task],
            process=Process.sequential,
            verbose=False
        )
        
        # Step 2: Get Relevance Examples (reusing interactive_main pattern)
        relevance_agent = student_crew.relevanceAgent()
        relevance_task = student_crew.relevanceTask()
        
        relevance_task.description = f"""
        Find real-world examples for: "{user_message}" in the context of {topic}
        {relevance_task.description.format(topic=topic)}
        """
        
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
        
        # Step 3: Generate Tutor Response (reusing interactive_main pattern)
        tutor_agent = student_crew.studentAgent()
        response_task = student_crew.studentTask()
        
        # Format conversation history for context (same as interactive_main)
        conversation_context = "\n".join([
            f"{msg['sender']}: {msg['content']}" 
            for msg in chat_history[-10:]
        ])
        
        response_task.description = f"""
        Respond to the student's question or comment: "{user_message}"
        
        Context from previous conversation:
        {conversation_context}
        
        Real-world examples to incorporate:
        {relevance_examples}
        
        {response_task.description.format(topic=topic)}
        
        Make sure to incorporate the real-world examples naturally into your response to help the student understand why this matters.
        """
        
        # Create crew for response generation (same as interactive_main)
        response_crew = Crew(
            agents=[tutor_agent],
            tasks=[response_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = response_crew.kickoff()
        return str(result)
        
    except Exception as e:
        return f"I encountered an error while processing your question. Please try rephrasing it. Error: {str(e)}"

def save_and_return_response(prisma_client, chat_session_id: str, user_message: str, 
                           agent_response: str, chat_history: List[Dict], student_context: Dict) -> Dict:
    """Save messages to database and return formatted response"""
    try:
        # Save user message to database
        run_async(prisma_client.add_message_to_session(
            session_id=chat_session_id,
            sender="student",
            content=user_message
        ))
        
        # Save agent response to database  
        run_async(prisma_client.add_message_to_session(
            session_id=chat_session_id,
            sender="tutor",
            content=agent_response
        ))
        
        # Add agent response to chat history
        chat_history.append({
            "sender": "tutor",
            "content": agent_response,
            "timestamp": None
        })
        
        return {
            "response": agent_response,
            "chat_history": chat_history,
            "student_context": {
                "name": student_context["student_name"],
                "learning_style": student_context["learning_style"],
                "grade": student_context["grade"]
            }
        }
        
    finally:
        # Disconnect from database
        run_async(prisma_client.disconnect())