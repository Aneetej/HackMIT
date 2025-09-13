#This file establishes the crew for the system.

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from langchain_anthropic import ChatAnthropic
from typing import List
import os

@CrewBase
class Studentagents():
    """Studentagents crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        super().__init__()
        # Initialize Claude LLM for student conversations
        self.student_llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7, 
        )
        
        # Initialize Claude LLM for analytics
        self.analyst_llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            #Low temperature allows for more focused and accurate analysis
            temperature=0.3,  
        )
        
        self.crew_llm = self.student_llm


    #Pull from yaml config file
    @agent
    def studentAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['studentAgent'],
            #Errors will show up if there are any
            verbose=True,
            llm=self.student_llm
        )

    #Pull from yaml config file
    @agent
    def studentAnalyst(self) -> Agent:
        return Agent(
            config=self.agents_config['studentAnalyst'],
            verbose=True,
            llm=self.analyst_llm
        )

    #Pull from yaml config file
    @task
    def studentTask(self) -> Task:
        return Task(
            config=self.tasks_config['studentTask']
        )

    #Pull from yaml config file
    @task
    def analystTask(self) -> Task:
        return Task(
            config=self.tasks_config['analystTask'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Studentagents crew"""
        
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            memory=True,
            manager_llm=self.crew_llm 
        )
