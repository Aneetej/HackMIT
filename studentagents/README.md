# Student Agents

An interactive AI tutoring system powered by [crewAI](https://crewai.com) and Claude. This project creates personalized learning experiences through conversational AI agents that adapt to individual student needs.

## Features

- **Interactive Tutoring**: Real-time conversations with AI tutors on any subject
- **Personalized Learning**: Agents adapt to student preferences and learning styles  
- **Conversation Analysis**: Automatic analysis of learning sessions with insights and recommendations
- **Multi-Agent System**: Student tutor and analyst agents working together

## Installation

Ensure you have Python >=3.10 <3.14 installed. This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

1. Install uv:

```bash
pip install uv
```

2. Navigate to the project directory and sync dependencies:

```bash
uv sync
```

3. Set up your environment variables in `.env`:

```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

## Usage

### Interactive Tutoring Session

Start an interactive tutoring session:

```bash
uv run python src/studentagents/interactive_main.py [subject]
```

Examples:
```bash
uv run python src/studentagents/interactive_main.py algebra
uv run python src/studentagents/interactive_main.py calculus
uv run python src/studentagents/interactive_main.py geometry
```

### Standard Crew Execution

Run the standard crew workflow:

```bash
crewai run
```

## Configuration

- **Agents**: Modify `src/studentagents/config/agents.yaml` to customize agent roles and behaviors
- **Tasks**: Modify `src/studentagents/config/tasks.yaml` to define learning objectives and outputs
- **Crew Logic**: Modify `src/studentagents/crew.py` for advanced customizations

## How It Works

1. **Student Agent**: Acts as an AI tutor, providing explanations, examples, and guidance
2. **Analyst Agent**: Analyzes learning sessions to identify strengths, struggles, and recommendations
3. **Interactive Mode**: Enables real-time conversations between students and AI tutors
4. **Analysis Output**: Generates detailed reports saved to `conversation_analysis.md`

## Support

For questions about this agentic setup, please contact Aneetej.
