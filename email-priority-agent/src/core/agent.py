"""
Email Priority AI Agent - Core Orchestrator
Uses LangGraph to coordinate multiple specialized agents
"""

from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
from datetime import datetime
import asyncio
from enum import Enum

from langgraph.graph import StateGraph, Graph
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import structlog

from ..memory.cognitive_memory import CognitiveMemorySystem
from ..memory.vector_store import VectorMemoryStore
from ..ingestion.email_ingestion import EmailIngestionAgent
from ..ingestion.sms_ingestion import SMSIngestionAgent
from ..classification.priority_classifier import PriorityClassificationAgent
from ..classification.importance_analyzer import ImportanceAnalyzer
from ..utils.config import get_settings

logger = structlog.get_logger()


class MessagePriority(Enum):
    """Priority levels for messages"""
    CRITICAL = "critical"      # Immediate action required
    HIGH = "high"              # Important and urgent
    MEDIUM = "medium"          # Important but not urgent
    LOW = "low"                # Can wait
    NOISE = "noise"            # Not important


class MessageState(TypedDict):
    """State object that flows through the agent graph"""
    message_id: str
    source: str  # 'email' or 'sms'
    raw_content: Dict[str, Any]
    parsed_content: Optional[Dict[str, Any]]
    sender_info: Optional[Dict[str, Any]]
    thread_context: Optional[List[Dict[str, Any]]]
    extracted_features: Optional[Dict[str, Any]]
    priority_score: Optional[float]
    importance_score: Optional[float]
    urgency_score: Optional[float]
    priority_level: Optional[MessagePriority]
    reasoning: Optional[str]
    memory_context: Optional[List[Dict[str, Any]]]
    processing_timestamp: datetime
    errors: List[str]


@dataclass
class ProcessedMessage:
    """Final processed message with priority information"""
    message_id: str
    source: str
    sender: str
    subject: Optional[str]
    preview: str
    priority_level: MessagePriority
    priority_score: float
    importance_score: float
    urgency_score: float
    reasoning: str
    received_at: datetime
    processed_at: datetime
    thread_id: Optional[str]
    tags: List[str]


class EmailPriorityAgent:
    """Main orchestrator agent using LangGraph"""
    
    def __init__(self, llm_provider: str = "openai"):
        self.settings = get_settings()
        self.logger = logger.bind(component="EmailPriorityAgent")
        
        # Initialize LLM
        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.2,
                api_key=self.settings.openai_api_key
            )
        else:
            self.llm = ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=0.2,
                api_key=self.settings.anthropic_api_key
            )
        
        # Initialize sub-agents
        self.memory_system = CognitiveMemorySystem()
        self.vector_store = VectorMemoryStore()
        self.email_ingestion = EmailIngestionAgent()
        self.sms_ingestion = SMSIngestionAgent()
        self.priority_classifier = PriorityClassificationAgent(self.llm)
        self.importance_analyzer = ImportanceAnalyzer(self.llm)
        
        # Build the agent graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(MessageState)
        
        # Add nodes for each processing step
        workflow.add_node("ingest", self._ingest_message)
        workflow.add_node("enrich_sender", self._enrich_sender_info)
        workflow.add_node("retrieve_thread", self._retrieve_thread_context)
        workflow.add_node("retrieve_memory", self._retrieve_memory_context)
        workflow.add_node("extract_features", self._extract_features)
        workflow.add_node("classify_priority", self._classify_priority)
        workflow.add_node("final_decision", self._make_final_decision)
        
        # Define the workflow edges
        workflow.set_entry_point("ingest")
        workflow.add_edge("ingest", "enrich_sender")
        workflow.add_edge("enrich_sender", "retrieve_thread")
        workflow.add_edge("retrieve_thread", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "extract_features")
        workflow.add_edge("extract_features", "classify_priority")
        workflow.add_edge("classify_priority", "final_decision")
        
        return workflow.compile()
    
    async def _ingest_message(self, state: MessageState) -> MessageState:
        """Ingest and parse the raw message"""
        try:
            if state["source"] == "email":
                parsed = await self.email_ingestion.parse_email(state["raw_content"])
            else:
                parsed = await self.sms_ingestion.parse_sms(state["raw_content"])
            
            state["parsed_content"] = parsed
            self.logger.info("Message ingested", 
                           message_id=state["message_id"],
                           source=state["source"])
        except Exception as e:
            state["errors"].append(f"Ingestion error: {str(e)}")
            self.logger.error("Ingestion failed", error=str(e))
            
        return state
    
    async def _enrich_sender_info(self, state: MessageState) -> MessageState:
        """Enrich sender information from various sources"""
        if not state["parsed_content"]:
            return state
            
        try:
            sender_email = state["parsed_content"].get("sender_email")
            if sender_email:
                # Retrieve sender history and importance
                sender_info = await self.memory_system.get_sender_profile(sender_email)
                state["sender_info"] = sender_info
                
                self.logger.info("Sender enriched",
                               sender=sender_email,
                               vip_status=sender_info.get("is_vip", False))
        except Exception as e:
            state["errors"].append(f"Sender enrichment error: {str(e)}")
            
        return state
    
    async def _retrieve_thread_context(self, state: MessageState) -> MessageState:
        """Retrieve thread/conversation context"""
        if not state["parsed_content"]:
            return state
            
        try:
            thread_id = state["parsed_content"].get("thread_id")
            if thread_id:
                # Get previous messages in thread
                thread_messages = await self.memory_system.get_thread_history(thread_id)
                state["thread_context"] = thread_messages
                
                self.logger.info("Thread context retrieved",
                               thread_id=thread_id,
                               message_count=len(thread_messages))
        except Exception as e:
            state["errors"].append(f"Thread retrieval error: {str(e)}")
            
        return state
    
    async def _retrieve_memory_context(self, state: MessageState) -> MessageState:
        """Retrieve relevant memories using vector similarity"""
        if not state["parsed_content"]:
            return state
            
        try:
            # Get content for embedding
            content = state["parsed_content"].get("content", "")
            subject = state["parsed_content"].get("subject", "")
            query_text = f"{subject} {content}"[:1000]  # Limit length
            
            # Search vector memory for similar contexts
            memories = await self.vector_store.search_similar_memories(
                query_text, 
                k=5,
                filters={"sender": state["parsed_content"].get("sender_email")}
            )
            
            state["memory_context"] = memories
            self.logger.info("Memory context retrieved", 
                           memory_count=len(memories))
        except Exception as e:
            state["errors"].append(f"Memory retrieval error: {str(e)}")
            
        return state
    
    async def _extract_features(self, state: MessageState) -> MessageState:
        """Extract features for classification"""
        if not state["parsed_content"]:
            return state
            
        try:
            features = {
                # Sender features
                "sender_importance": state["sender_info"].get("importance_score", 0.5) if state["sender_info"] else 0.5,
                "sender_is_vip": state["sender_info"].get("is_vip", False) if state["sender_info"] else False,
                "sender_response_rate": state["sender_info"].get("response_rate", 0.5) if state["sender_info"] else 0.5,
                
                # Content features
                "has_deadline": self._has_deadline_keywords(state["parsed_content"].get("content", "")),
                "has_action_items": self._has_action_keywords(state["parsed_content"].get("content", "")),
                "sentiment_urgency": await self._analyze_urgency_sentiment(state["parsed_content"].get("content", "")),
                
                # Thread features
                "is_thread_active": len(state["thread_context"] or []) > 2,
                "thread_response_time": self._calculate_thread_response_time(state["thread_context"]),
                
                # Temporal features
                "time_of_day_score": self._get_time_of_day_score(state["processing_timestamp"]),
                "day_of_week_score": self._get_day_of_week_score(state["processing_timestamp"]),
            }
            
            state["extracted_features"] = features
            self.logger.info("Features extracted", features=features)
        except Exception as e:
            state["errors"].append(f"Feature extraction error: {str(e)}")
            
        return state
    
    async def _classify_priority(self, state: MessageState) -> MessageState:
        """Classify message priority using specialized agent"""
        if not state["parsed_content"] or not state["extracted_features"]:
            return state
            
        try:
            # Use priority classification agent
            classification = await self.priority_classifier.classify(
                content=state["parsed_content"],
                features=state["extracted_features"],
                sender_info=state["sender_info"],
                thread_context=state["thread_context"],
                memory_context=state["memory_context"]
            )
            
            state["priority_score"] = classification["priority_score"]
            state["importance_score"] = classification["importance_score"]
            state["urgency_score"] = classification["urgency_score"]
            state["reasoning"] = classification["reasoning"]
            
            self.logger.info("Priority classified",
                           priority_score=classification["priority_score"],
                           importance=classification["importance_score"],
                           urgency=classification["urgency_score"])
        except Exception as e:
            state["errors"].append(f"Classification error: {str(e)}")
            
        return state
    
    async def _make_final_decision(self, state: MessageState) -> MessageState:
        """Make final priority decision"""
        try:
            # Determine priority level based on scores
            priority_score = state.get("priority_score", 0.5)
            
            if priority_score >= 0.9:
                state["priority_level"] = MessagePriority.CRITICAL
            elif priority_score >= 0.75:
                state["priority_level"] = MessagePriority.HIGH
            elif priority_score >= 0.5:
                state["priority_level"] = MessagePriority.MEDIUM
            elif priority_score >= 0.25:
                state["priority_level"] = MessagePriority.LOW
            else:
                state["priority_level"] = MessagePriority.NOISE
                
            # Store the decision in memory for learning
            await self.memory_system.store_priority_decision(
                message_id=state["message_id"],
                decision=state["priority_level"],
                scores={
                    "priority": state.get("priority_score", 0),
                    "importance": state.get("importance_score", 0),
                    "urgency": state.get("urgency_score", 0)
                },
                reasoning=state.get("reasoning", "")
            )
            
            self.logger.info("Final decision made",
                           message_id=state["message_id"],
                           priority_level=state["priority_level"].value)
        except Exception as e:
            state["errors"].append(f"Decision error: {str(e)}")
            state["priority_level"] = MessagePriority.MEDIUM  # Default
            
        return state
    
    async def process_message(self, 
                            message_id: str,
                            source: str,
                            raw_content: Dict[str, Any]) -> ProcessedMessage:
        """Process a single message through the agent graph"""
        
        # Initialize state
        initial_state: MessageState = {
            "message_id": message_id,
            "source": source,
            "raw_content": raw_content,
            "parsed_content": None,
            "sender_info": None,
            "thread_context": None,
            "extracted_features": None,
            "priority_score": None,
            "importance_score": None,
            "urgency_score": None,
            "priority_level": None,
            "reasoning": None,
            "memory_context": None,
            "processing_timestamp": datetime.utcnow(),
            "errors": []
        }
        
        # Run through the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Convert to ProcessedMessage
        parsed = final_state.get("parsed_content", {})
        return ProcessedMessage(
            message_id=message_id,
            source=source,
            sender=parsed.get("sender_email", "Unknown"),
            subject=parsed.get("subject"),
            preview=parsed.get("preview", "")[:200],
            priority_level=final_state.get("priority_level", MessagePriority.MEDIUM),
            priority_score=final_state.get("priority_score", 0.5),
            importance_score=final_state.get("importance_score", 0.5),
            urgency_score=final_state.get("urgency_score", 0.5),
            reasoning=final_state.get("reasoning", "No reasoning available"),
            received_at=parsed.get("received_at", datetime.utcnow()),
            processed_at=datetime.utcnow(),
            thread_id=parsed.get("thread_id"),
            tags=parsed.get("tags", [])
        )
    
    async def process_new_messages(self) -> List[ProcessedMessage]:
        """Process all new messages from configured sources"""
        results = []
        
        # Get new emails
        new_emails = await self.email_ingestion.fetch_new_emails()
        for email in new_emails:
            try:
                processed = await self.process_message(
                    message_id=email["id"],
                    source="email",
                    raw_content=email
                )
                results.append(processed)
            except Exception as e:
                self.logger.error("Failed to process email", 
                                email_id=email["id"], 
                                error=str(e))
        
        # Get new SMS messages
        new_sms = await self.sms_ingestion.fetch_new_sms()
        for sms in new_sms:
            try:
                processed = await self.process_message(
                    message_id=sms["id"],
                    source="sms",
                    raw_content=sms
                )
                results.append(processed)
            except Exception as e:
                self.logger.error("Failed to process SMS",
                                sms_id=sms["id"],
                                error=str(e))
        
        return results
    
    def get_urgent_messages(self, threshold: float = 0.8) -> List[ProcessedMessage]:
        """Get messages above urgency threshold"""
        # This would typically query from a database
        # For now, returning empty list as placeholder
        return []
    
    # Helper methods
    def _has_deadline_keywords(self, content: str) -> bool:
        """Check if content contains deadline-related keywords"""
        keywords = ["deadline", "due", "by tomorrow", "urgent", "asap", 
                   "end of day", "eod", "cob", "time sensitive"]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in keywords)
    
    def _has_action_keywords(self, content: str) -> bool:
        """Check if content contains action-related keywords"""
        keywords = ["please", "could you", "can you", "need", "require",
                   "action required", "response needed", "waiting for"]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in keywords)
    
    async def _analyze_urgency_sentiment(self, content: str) -> float:
        """Analyze urgency sentiment of content"""
        # Simplified - in production would use NLP model
        urgency_words = ["urgent", "asap", "immediately", "critical", "emergency"]
        content_lower = content.lower()
        urgency_count = sum(1 for word in urgency_words if word in content_lower)
        return min(urgency_count / 3.0, 1.0)  # Normalize to 0-1
    
    def _calculate_thread_response_time(self, thread_context: Optional[List[Dict]]) -> float:
        """Calculate average response time in thread"""
        if not thread_context or len(thread_context) < 2:
            return 0.5
        
        # Simplified calculation
        # In production would analyze actual timestamps
        return 0.7  # Placeholder
    
    def _get_time_of_day_score(self, timestamp: datetime) -> float:
        """Score based on time of day (business hours = higher)"""
        hour = timestamp.hour
        if 9 <= hour <= 17:  # Business hours
            return 1.0
        elif 6 <= hour <= 22:  # Waking hours
            return 0.7
        else:  # Night time
            return 0.3
    
    def _get_day_of_week_score(self, timestamp: datetime) -> float:
        """Score based on day of week (weekdays = higher)"""
        weekday = timestamp.weekday()
        if weekday < 5:  # Monday-Friday
            return 1.0
        else:  # Weekend
            return 0.6