#This file is used to run the interactive conversation between the student and the tutor.

#!/usr/bin/env python
import os
import sys
import yaml
from crewai import Task, Crew, Process
from studentagents.crew import Studentagents


def interactive_conversation(topic: str = "algebra"):
    """Run an interactive conversation between student and tutor"""
    print(f" Interactive {topic.title()} Tutor")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'help' for assistance")
    print("-" * 50)
    
    # Create the Studentagents crew
    student_crew = Studentagents()
    
    # Get the agents from the crew
    tutor_agent = student_crew.studentAgent()
    analyst_agent = student_crew.studentAnalyst()
    
    # Store conversation history
    conversation_history = []
    
    print(f"\n Tutor: Hello! I'm your {topic} expert. What would you like to learn about today?")
    
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
            print("Type your question or topic you'd like to explore!")
            continue
        elif not student_input:
            print("Please type your question or 'quit' to exit.")
            continue
        
        # Store student message
        conversation_history.append(f"Student: {student_input}")
        
        # Create a task for the tutor to respond using the crew's task configuration
        response_task = Task(
            description=f"""
            Respond to the student's question or comment: "{student_input}"
            
            Context from previous conversation:
            {chr(10).join(conversation_history[-10:])}  # Last 10 messages for context
            
            Converse with the student and assist them in learning {topic}. Ensure you are presenting the material in the way the student prefers.
            Provide a helpful, clear, and engaging response.
            If they ask a question, answer it thoroughly.
            If they need examples, provide them.
            If they're struggling, offer encouragement and break things down.
            """,
            expected_output="The student should be able to understand the material and be able to apply it to real-world problems.",
            agent=tutor_agent
        )
        
        # Create a simple crew to execute the task
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
                print(f"\n Sorry, I encountered an error: {e}")
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
    
    # Create analysis task using the crew's task configuration
    analysis_task = Task(
        description=f"""
        Analyze the student's conversation and summarize their interaction. Determine the frequently asked questions, topics where the student was struggling, and suggestions for the teacher when updating lesson plans.
        
        Conversation to analyze:
        {chr(10).join(conversation_history)}
        
        Provide a summary that includes:
        1. Main topics discussed
        2. Student's level of understanding
        3. Areas where the student struggled
        4. Areas where the student showed strength
        5. Suggestions for future learning
        6. Overall engagement assessment
        """,
        expected_output="A one paragraph summary of the interaction with all relevant information. Must be less than 250 words.",
        agent=analyst_agent,
        output_file="conversation_analysis.md"
    )
    
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
