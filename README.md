# HackMIT 2025 Project

Welcome to the HackMIT repository! This project was created for HackMIT 2025 and showcases an advanced tech stack integrating modern AI APIs and agent frameworks. Below you'll find a comprehensive overview of the tech stack and the AI APIs leveraged, including Anthropic Claude, Exa, Cerebras, and CrewAI.

---

## 🛠️ Tech Stack

**Primary Language:** Python

**Frameworks & Libraries:**
- FastAPI / Flask (for API endpoints and backend integration)
- CrewAI (multi-agent orchestration)
- LangChain, LlamaIndex (for RAG/document retrieval, optional)
- Other Python libraries for async, data handling, and web requests

**AI API Integrations:**
- **Anthropic Claude**: Used for natural language understanding, long-context chat, and advanced reasoning tasks. Supports models such as Claude 3 Sonnet, Opus, and Haiku. API calls are authenticated via `x-api-key`, and Python SDKs are leveraged for streaming and batch completions [[Anthropic Claude API docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)].
- **Cerebras**: Integrates Cerebras-GPT and other LLMs for high-throughput inference and training tasks. Supports models via their cloud SDK and can run large-scale jobs (LLaMA, GPT) on wafer-scale hardware [[Cerebras API docs](https://docs.cerebras.net/en/latest/)].
- **Exa**: Used for advanced semantic web search and retrieval, enabling agents to query the latest information and datasets from the web efficiently [[Exa docs](https://exa.ai)].
- **CrewAI**: Agent orchestration framework that coordinates multiple AI agents (e.g., document search, report writing, data analysis) for collaborative problem-solving. Enables complex workflows with human-in-the-loop and custom tool integrations [[CrewAI GitHub](https://github.com/joaomdmoura/crewAI)].

**Other Supported AI Providers:**
- OpenAI (GPT-4, GPT-4o)
- Gemini, Groq, Mistral, Cohere, Meta Llama, and more (via unified SDKs)

---

## 🤖 Example AI Agent Workflow

1. **User submits a query or uploads data**
2. **CrewAI orchestrates agents**:
    - Claude handles complex reasoning and language tasks.
    - Exa agent fetches and semantically ranks web/document data.
    - Cerebras agent runs large-scale model inference for analysis.
    - Custom Python tools execute code and data processing.
3. **Results are aggregated and presented to the user**.

---

## 🔗 Key API Call Examples

```python
# Anthropic Claude call (Python)
import anthropic
client = anthropic.Client(api_key='YOUR_ANTHROPIC_API_KEY')
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "Explain AI safety in 100 words."}],
)

# Cerebras GPT call
from cerebras.cloud.sdk import Client
client = Client(api_key='YOUR_CEREBRAS_API_KEY')
completion = client.completions.create(model="cerebras/llama3.1-8b", prompt="Analyze dataset trends.")

# CrewAI agent setup
from crewai import Agent, Crew, Task
agent = Agent(name="Researcher", description="Find latest AI techniques", tools=[ExaTool()])
crew = Crew(agents=[agent], tasks=[Task(...)])

# Exa semantic search (pseudo-code)
results = exa.search("latest developments in AI agents")
```

---

## 🧠 AI Agent Frameworks & Capabilities

- **CrewAI** enables multi-agent workflows, where agents can use external APIs like Claude and Cerebras, or tools like Exa for web search.
- **Function Calling & Tool Use**: Agents can call Python functions or external APIs to retrieve structured data, analyze reports, or generate summaries.
- **Streaming & Async Support**: Many APIs support streaming output for real-time feedback.

---

## 📚 References & Learning Resources

- [CrewAI Docs](https://docs.crewai.com/)
- [Anthropic Claude API Docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Cerebras Documentation](https://docs.cerebras.net/en/latest/)
- [Exa.ai](https://exa.ai)
- [Multi-Agent Systems with CrewAI (DeepLearning.AI)](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/)
- [RAG Agents Bootcamp (AI Planet)](https://aiplanet.com/courses/rag-agents-bootcamp)

---

## ✨ Project Highlights

- Leverages multiple state-of-the-art AI APIs for robust, scalable, and secure agent-based solutions.
- Modular, extensible agent architecture using CrewAI.
- Supports advanced document retrieval, semantic web search, and natural language reasoning.
- Designed for hackathon-grade experimentation and real-world AI use cases.

---
