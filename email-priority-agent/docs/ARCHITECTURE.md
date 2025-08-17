# Email Priority AI Agent - Architecture Documentation

## Overview

This document describes the architecture of an advanced AI agent system for prioritizing emails and SMS messages. The system uses state-of-the-art agent frameworks, cognitive memory systems, and large language models to intelligently classify messages based on importance and urgency.

## Key Innovations

### 1. **Multi-Agent Architecture with LangGraph**
- Uses LangGraph for orchestrating multiple specialized agents
- Graph-based workflow ensures proper state management and error handling
- Each agent has a specific responsibility in the processing pipeline

### 2. **Cognitive Memory System (Inspired by A-MEM and CAIM)**
- **Multi-Tiered Memory Architecture**:
  - Working Memory (immediate context, ~20 items)
  - Short-Term Memory (recent interactions, ~100 items)
  - Long-Term Memory (persistent knowledge)
  - Episodic Memory (specific events and decisions)
- **Dynamic Memory Consolidation**: Automatic promotion of important memories
- **Spreading Activation**: Related memories are activated together
- **Memory Connections**: Graph-based memory associations

### 3. **Vector-Based Semantic Search**
- Qdrant vector database for efficient similarity search
- Embeddings for all messages and memories
- Knowledge graph connections between related memories
- Cross-collection search capabilities

### 4. **Intelligent Priority Classification**
- Combines LLM analysis with rule-based adjustments
- Separate importance (long-term value) and urgency (time sensitivity) scores
- Context-aware classification using thread history and sender profiles
- Continuous learning from user feedback

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interface Layer                       │
│  - Web Dashboard (React + TypeScript)                       │
│  - Real-time Notifications                                  │
│  - Priority Message View                                    │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  - REST Endpoints                                           │
│  - WebSocket for Real-time Updates                         │
│  - Authentication & Authorization                          │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Agent Orchestration                   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                  Main Workflow Graph                  │  │
│  │  1. Message Ingestion → 2. Sender Enrichment        │  │
│  │  3. Thread Retrieval → 4. Memory Retrieval          │  │
│  │  5. Feature Extraction → 6. Priority Classification  │  │
│  │  7. Final Decision & Storage                         │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   Specialized Agents                         │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Ingestion   │Classification│   Memory     │   Learning    │
│   Agents     │    Agent     │   Agent      │    Agent      │
│ - Email      │ - Priority   │ - Storage    │ - Feedback    │
│ - SMS        │ - Importance │ - Retrieval  │ - Adaptation  │
└──────────────┴──────────────┴──────────────┴───────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    Core Services                             │
├──────────────┬──────────────┬──────────────┬───────────────┤
│     LLM      │  Embeddings  │   Database   │    Cache      │
│  - OpenAI    │  - OpenAI    │ - PostgreSQL │  - Redis      │
│  - Anthropic │  - Custom    │ - Qdrant     │               │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## Component Details

### 1. Message Ingestion Pipeline

**Email Ingestion Agent**:
- Connects via IMAP to email providers
- Parses email structure (headers, body, attachments)
- Extracts metadata and threading information
- Handles various email formats (plain text, HTML, multipart)

**SMS Ingestion Agent**:
- Integrates with Twilio API
- Processes SMS metadata
- Links related messages into conversations

### 2. Memory System Components

**Cognitive Memory System**:
```python
class CognitiveMemorySystem:
    - Working Memory: Deque with size limit
    - Short-Term Memory: Dictionary with decay
    - Memory Controller: Handles consolidation
    - Spreading Activation: Graph-based retrieval
```

**Vector Memory Store**:
- Qdrant collections for different memory types
- Semantic search across memories
- Knowledge graph connections
- Importance score updates

### 3. Classification System

**Feature Extraction**:
- Sender features (importance, VIP status, response rate)
- Content features (deadlines, action items, sentiment)
- Thread features (activity level, response time)
- Temporal features (time of day, day of week)

**Priority Classification Agent**:
- LLM-based analysis with structured output
- Rule-based adjustments for special cases
- Separate importance and urgency scoring
- Clear reasoning and factor identification

### 4. Learning and Adaptation

**Continuous Learning**:
- Stores all decisions as episodic memories
- Tracks user feedback and corrections
- Updates sender profiles based on interactions
- Adjusts classification weights over time

**Feedback Loop**:
```
User Action → Episodic Memory → Pattern Analysis → 
Weight Adjustment → Improved Classification
```

## Data Flow

1. **Message Arrival**:
   ```
   Email/SMS → Ingestion → Parsing → Initial Storage
   ```

2. **Enrichment Phase**:
   ```
   Message → Sender Profile Lookup → Thread Context → 
   Memory Search → Feature Extraction
   ```

3. **Classification Phase**:
   ```
   Features + Context → LLM Analysis → Score Calculation → 
   Rule Adjustments → Final Priority
   ```

4. **Memory Update**:
   ```
   Decision → Working Memory → Consolidation → 
   Long-term Storage → Vector Index Update
   ```

## Memory Architecture Deep Dive

### Memory Tiers

1. **Working Memory**:
   - Capacity: 20 items
   - Storage: In-memory deque
   - Purpose: Immediate context for current processing
   - Retention: Minutes

2. **Short-Term Memory**:
   - Capacity: 100 items
   - Storage: In-memory dictionary
   - Purpose: Recent interactions and decisions
   - Retention: Hours to days

3. **Long-Term Memory**:
   - Capacity: Unlimited
   - Storage: PostgreSQL + Qdrant
   - Purpose: Persistent knowledge and patterns
   - Retention: Permanent

4. **Episodic Memory**:
   - Capacity: Unlimited
   - Storage: PostgreSQL
   - Purpose: Specific events and decisions
   - Retention: Permanent

### Memory Consolidation Process

```python
async def consolidate_memories():
    1. Sort working memory by importance + recency
    2. Move overflow to short-term memory
    3. Evaluate short-term memory for persistence
    4. Store important memories to long-term
    5. Update vector embeddings
    6. Create knowledge graph connections
```

### Spreading Activation Algorithm

```python
def spreading_activation(seed_memories, initial_activations):
    1. Initialize activation scores with seeds
    2. For each memory:
       - Spread activation to connected memories
       - Apply decay factor (0.7)
       - Continue until threshold (0.1)
    3. Combine activated memories
    4. Sort by final activation score
```

## Priority Classification Algorithm

### Score Calculation

```
Priority Score = (Importance × 0.5) + (Urgency × 0.5)

Where:
- Importance = f(sender_value, content_value, relationship)
- Urgency = f(deadlines, keywords, thread_activity, time_factors)
```

### Classification Rules

1. **VIP Sender Boost**: +0.2 priority, +0.3 importance
2. **Deadline Detection**: +0.3 urgency, +0.2 priority
3. **Active Thread**: +0.1 urgency
4. **Low Sender Importance**: -0.2 priority
5. **Time-based Adjustments**: Business hours boost

## Performance Optimizations

1. **Async Processing**: All I/O operations are asynchronous
2. **Batch Operations**: Messages processed in batches
3. **Caching**: Redis for frequently accessed data
4. **Vector Indexing**: HNSW algorithm in Qdrant
5. **Connection Pooling**: Database connection reuse

## Security Considerations

1. **API Key Management**: Environment variables, never in code
2. **Email Credentials**: Encrypted storage
3. **Data Privacy**: PII handling compliance
4. **Access Control**: Role-based permissions
5. **Audit Logging**: All decisions tracked

## Deployment Architecture

### Development
```
Docker Compose:
- Application containers
- PostgreSQL
- Redis  
- Qdrant
- Development tools
```

### Production
```
Kubernetes:
- Application pods with HPA
- Managed PostgreSQL (RDS/Cloud SQL)
- Managed Redis (ElastiCache/Memorystore)
- Qdrant cluster
- Load balancer
- Monitoring stack
```

## Monitoring and Observability

1. **Metrics** (Prometheus):
   - Message processing rate
   - Classification accuracy
   - Memory usage
   - API latency

2. **Logging** (Structured with Structlog):
   - All classification decisions
   - Error tracking
   - Performance metrics

3. **Tracing** (OpenTelemetry):
   - Full request lifecycle
   - Agent execution flow
   - External service calls

## Future Enhancements

1. **Multi-Modal Processing**: 
   - Attachment analysis
   - Image recognition for screenshots

2. **Advanced Learning**:
   - Reinforcement learning from feedback
   - Transfer learning between users

3. **Proactive Insights**:
   - Pattern detection
   - Anomaly alerting
   - Predictive prioritization

4. **Integration Expansion**:
   - Slack/Teams messages
   - Calendar integration
   - Task management systems

## Conclusion

This architecture provides a sophisticated, scalable solution for email and SMS prioritization. The combination of cognitive memory systems, multi-agent orchestration, and continuous learning creates an intelligent system that improves over time and adapts to user needs.