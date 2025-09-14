#This file is used to run the interactive conversation between the student and the tutor.

#!/usr/bin/env python
import os
import sys
import yaml
from crewai import Task, Crew, Process
from studentagents.crew import Studentagents

#from studentagents.database_utils import get_student_data 
#TODO: Replace def create_defalt_student_context one db is connected

def create_default_student_context():
    """Create default student context when database is unavailable"""
    return {
        'learning_style': 'visual',
        'student_name': 'Student',
        'grade': '10',
        'subject_focus': 'algebra',
        'preferred_content': 'interactive',
        'concepts_mastered': 'basic arithmetic',
        'improvement_areas': 'word problems',
        'total_sessions': 1,
        'total_messages': 0,
        'total_time_spent': 0,
        'average_engagement': 75,
        'teacher_name': 'Teacher',
        'class_name': 'Demo Class',
        'teaching_style': 'interactive'
    }

def interactive_conversation(topic: str = "algebra"):
    """Run an interactive conversation between student and tutor"""

    #Replace this line with student_context once db is connected
    #student_context = get_student_data()
    # Use default student context (no database dependency)
    student_context = create_default_student_context()
    
    print(f"\n Interactive {topic.title()} Tutor")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'help' for assistance")
    print("-" * 50)
    
    # Create the Studentagents crew with student context
    student_crew = Studentagents(student_context=student_context)
    
    # Get the agents from the crew
    tutor_agent = student_crew.studentAgent()
    analyst_agent = student_crew.studentAnalyst()
    
    # Store conversation history
    conversation_history = []
    
    print(f"\n Tutor: Hello! I'm your {topic} expert. What would you like to learn about today?")
    print({preferred_content})
    while True:
        # Get student input
        student_input = input("\n You: ").strip()
        
        if student_input.lower() in ['quit', 'exit', 'bye']:
            print("\n Lunara: Great session! Let me analyze our conversation...")
            print(f"Debug: Conversation history has {len(conversation_history)} entries")
            break
        elif student_input.lower() == 'help':
            print("\n Lunara: I can help you with:")
            print(f"- {topic.title()} concepts and problems")
            print("- Step-by-step explanations")
            print("- Practice problems")
            print("- Study tips and strategies")
            print(f"- Content adapted for your {student_context['learning_style']} learning style")
            print("Type your question or topic you'd like to explore!")
            continue
        elif not student_input:
            print("Please type your question or 'quit' to exit.")
            continue
        
        # Store student message
        conversation_history.append(f"Student: {student_input}")
        

        # Step 1: Guideline Check - Stop if homework question detected
        guideline_agent = student_crew.guidelineAgent()
        guideline_task = student_crew.guidelineTask()
        
        # Execute guideline check --  feature addition
        guideline_crew = Crew(
            agents=[guideline_agent],
            tasks=[guideline_task],
            process=Process.sequential,
            verbose=False
        )

      
        
        # Step 2: Get Relevance Examples
        print("\n Finding relevant examples...")
        relevance_agent = student_crew.relevanceAgent()
        relevance_task = student_crew.relevanceTask()
        
        # Enhance relevance task with current input
        relevance_task.description = f"""
        Find real-world examples for: "{student_input}" in the context of {topic}
        
        {relevance_task.description.format(topic=topic)}
        """
        
        relevance_examples = ""
        try:
            # Execute relevance search
            relevance_crew = Crew(
                agents=[relevance_agent],
                tasks=[relevance_task],
                process=Process.sequential,
                verbose=False
            )
            
            relevance_result = relevance_crew.kickoff()
            relevance_examples = str(relevance_result)
            
        except Exception as e:
            print(f"\n Relevance search failed: {e}")
            relevance_examples = "No additional examples found at this time."
        
        # Step 3: Tutor Response with Relevance Examples
        print("\n Generating personalized response...")
        response_task = student_crew.studentTask()
        
        # Enhance the task description with current context and relevance examples
        response_task.description = f"""
        Respond to the student's question or comment: "{student_input}"
        
        Context from previous conversation:
        {chr(10).join(conversation_history[-10:])}  # Last 10 messages for context
        
        Real-world examples to incorporate:
        {relevance_examples}
        
        {response_task.description.format(topic=topic)}
        
        Make sure to incorporate the real-world examples naturally into your response to help the student understand why this matters.
        """
        
        # Create a crew to execute the enhanced task
        crew = Crew(
            agents=[tutor_agent],
            tasks=[response_task],
            process=Process.sequential,
            verbose=False
        )
        
        try:
            # Get the tutor's response
            result = crew.kickoff()
            tutor_response = str(result)
            
            # Display the response
            print(f"\n Lunara: {tutor_response}")
            
            # Store tutor response
            conversation_history.append(f"Lunara: {tutor_response}")
            
        except Exception as e:
            # Filter out connection reset errors that don't affect functionality
            error_str = str(e)
            if "Connection aborted" not in error_str and "ConnectionResetError" not in error_str:
                print(f"\n Error generating response: {e}")
                print("Please try rephrasing your question.")
    
    return conversation_history

def analyze_conversation(conversation_history: list, topic: str):
    """Analyze the completed conversation using the crew's analyst agent"""
    if not conversation_history:
        print("No conversation to analyze.")
        return
    
    print("\n Analyzing conversation...")
    
    # Create the Studentagents crew
    student_crew = Studentagents()
    
    # Get the analyst agent from the crew
    analyst_agent = student_crew.studentAnalyst()
    
    # Get the analyst task from YAML configuration
    analysis_task = student_crew.analystTask()
    
    # Enhance the task description with conversation data
    analysis_task.description = f"""
    {analysis_task.description.format(topic=topic)}
    
    Conversation to analyze:
    {chr(10).join(conversation_history)}
    """
    analysis_task.output_file = "conversation_analysis.md"
    
    # Create crew for analysis
    analysis_crew = Crew(
        agents=[analyst_agent],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True
    )
    
    try:
        analysis_result = analysis_crew.kickoff()
        print(f"\n Session Analysis:")
        print("-" * 30)
        print(analysis_result)
        print(f"\n Analysis saved to: conversation_analysis.md")
        
    except Exception as e:
        print(f" Error during analysis: {e}")

def main():
    """Main interactive function"""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set your Anthropic API key in the .env file:")
        print("ANTHROPIC_API_KEY=your-api-key-here")
        return
    
    # Get topic from command line or use default
    topic = sys.argv[1] if len(sys.argv) > 1 else "algebra"
    
    try:
        # Run interactive conversation
        conversation_history = interactive_conversation(topic)
        
        # Analyze the conversation
        print(f"Debug: Final conversation history has {len(conversation_history)} entries")
        if conversation_history:
            print("Debug: Running analysis...")
            analyze_conversation(conversation_history, topic)
        else:
            print("Debug: No conversation history to analyze")
        
        print("\n Session completed!")
        
    except KeyboardInterrupt:
        print("\n\n Session interrupted. Goodbye!")
    except Exception as e:
        print(f"\n An error occurred: {e}")

if __name__ == "__main__":
    main()
