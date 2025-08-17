# Quick Start Guide

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL 14+
- Redis 6+
- Qdrant (via Docker)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/email-priority-agent.git
cd email-priority-agent
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configure API Keys

Edit `.env` and add your API keys:
- OpenAI or Anthropic API key for LLM
- Email credentials (Gmail app-specific password recommended)
- Twilio credentials (if using SMS)

### 4. Start Services

```bash
# Start infrastructure services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Initialize database
python scripts/init_db.py
```

### 5. Run the Agent

```bash
# Start the agent
python -m src.main

# Or run with auto-reload for development
uvicorn src.api.main:app --reload
```

## Basic Usage

### Process New Messages

```python
from src.core.agent import EmailPriorityAgent

# Initialize agent
agent = EmailPriorityAgent()

# Process new messages
messages = await agent.process_new_messages()

# Get high-priority messages
urgent = agent.get_urgent_messages(threshold=0.8)
```

### API Endpoints

```bash
# Get priority messages
curl http://localhost:8000/api/messages/priority

# Process new messages manually
curl -X POST http://localhost:8000/api/messages/process

# Get sender profile
curl http://localhost:8000/api/senders/email@example.com
```

## Configuration

### Add VIP Senders

Edit `config/settings.yaml`:
```yaml
vip_emails:
  - important@example.com
  - boss@company.com
```

### Customize Priority Rules

```yaml
keyword_rules:
  urgent_keywords:
    - "deadline"
    - "urgent"
    boost: 0.4
```

## Troubleshooting

### Common Issues

1. **Connection Error to Qdrant**
   ```bash
   # Ensure Qdrant is running
   docker ps | grep qdrant
   ```

2. **Email Authentication Failed**
   - Use app-specific password for Gmail
   - Enable IMAP in Gmail settings
   - Check firewall settings

3. **Memory Issues**
   - Adjust `WORKING_MEMORY_SIZE` in `.env`
   - Increase consolidation interval

## Next Steps

- Read the full [Architecture Documentation](ARCHITECTURE.md)
- Customize priority rules in `config/settings.yaml`
- Set up monitoring with Prometheus
- Deploy to production using Kubernetes

## Support

- GitHub Issues: [Report bugs or request features]
- Documentation: [Full documentation]
- Community: [Join our Discord]