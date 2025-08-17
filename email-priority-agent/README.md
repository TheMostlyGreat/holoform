# Email Priority AI Agent

An advanced AI agent that intelligently prioritizes emails and SMS messages based on importance and urgency, using cutting-edge agent frameworks, LLMs, and memory systems.

## Overview

This agent goes beyond traditional spam filtering to identify truly important and urgent communications based on:
- Sender importance and relationship history
- Topic relevance and content analysis
- Thread context and conversation history
- Temporal factors and deadlines
- Historical interaction patterns

## Key Features

- **Multi-Agent Architecture**: Uses LangGraph for orchestrating multiple specialized agents
- **Advanced Memory System**: Implements a cognitive memory framework with working, short-term, long-term, and episodic memory
- **Semantic Understanding**: Leverages state-of-the-art LLMs for deep content analysis
- **Vector-Based Retrieval**: Uses embeddings and vector databases for efficient similarity search
- **Real-time Processing**: Processes messages as they arrive with minimal latency
- **Adaptive Learning**: Continuously improves based on user feedback and behavior

## Technology Stack

- **Framework**: LangGraph (built on LangChain) for agent orchestration
- **LLM**: OpenAI GPT-4 / Anthropic Claude for natural language understanding
- **Vector Database**: Qdrant for embedding storage and similarity search
- **Memory System**: Custom implementation inspired by A-MEM and CAIM frameworks
- **Message Ingestion**: IMAP/Gmail API for emails, Twilio API for SMS
- **Backend**: FastAPI for REST API
- **Frontend**: React with TypeScript for user interface
- **Database**: PostgreSQL for structured data, Redis for caching

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
├─────────────────────────────────────────────────────────────┤
│                    Notification System                       │
├─────────────────────────────────────────────────────────────┤
│                   LangGraph Orchestrator                     │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Ingestion  │ Classification│   Memory     │  Learning     │
│    Agent     │    Agent      │   Agent      │   Agent       │
├──────────────┴──────────────┴──────────────┴───────────────┤
│                    Core Services Layer                       │
├──────────────┬──────────────┬──────────────┬───────────────┤
│     LLM      │   Vector DB   │  Traditional │   Message     │
│   Service    │   (Qdrant)    │   Database   │   Brokers    │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/email-priority-agent.git
cd email-priority-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Initialize the database
python scripts/init_db.py

# Run the application
python -m src.main
```

## Configuration

Edit `config/settings.yaml` to configure:
- Email/SMS provider credentials
- LLM API keys
- Priority thresholds
- Memory system parameters
- User preferences

## Usage

```python
from src.core.agent import EmailPriorityAgent

# Initialize the agent
agent = EmailPriorityAgent()

# Process incoming messages
results = await agent.process_new_messages()

# Get high-priority messages
urgent_messages = agent.get_urgent_messages(threshold=0.8)
```

## Contributing

Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.