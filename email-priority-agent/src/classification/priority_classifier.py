"""
Priority Classification Agent
Uses LLM and multi-factor analysis to classify message priority
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import asyncio

from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field
import structlog

from ..utils.prompts import PRIORITY_CLASSIFICATION_PROMPT

logger = structlog.get_logger()


class PriorityClassification(BaseModel):
    """Output schema for priority classification"""
    priority_score: float = Field(
        description="Overall priority score from 0.0 to 1.0",
        ge=0.0, le=1.0
    )
    importance_score: float = Field(
        description="Importance score (long-term value) from 0.0 to 1.0",
        ge=0.0, le=1.0
    )
    urgency_score: float = Field(
        description="Urgency score (time sensitivity) from 0.0 to 1.0",
        ge=0.0, le=1.0
    )
    reasoning: str = Field(
        description="Detailed reasoning for the classification"
    )
    key_factors: List[str] = Field(
        description="Key factors that influenced the decision"
    )
    suggested_action: str = Field(
        description="Suggested action for handling this message"
    )


class PriorityClassificationAgent:
    """
    Intelligent agent for classifying message priority
    Combines multiple signals to determine importance and urgency
    """
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.logger = logger.bind(component="PriorityClassificationAgent")
        self.output_parser = PydanticOutputParser(pydantic_object=PriorityClassification)
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=PRIORITY_CLASSIFICATION_PROMPT),
            HumanMessage(content="""
Analyze this message and classify its priority:

Message Content:
{content}

Extracted Features:
{features}

Sender Information:
{sender_info}

Thread Context:
{thread_context}

Memory Context:
{memory_context}

{format_instructions}

Consider the following factors:
1. Sender importance and relationship
2. Content urgency indicators
3. Action requirements
4. Thread activity and response patterns
5. Historical interaction patterns
6. Time sensitivity
7. Business impact

Provide a comprehensive analysis with clear reasoning.
            """)
        ])
        
    async def classify(self,
                      content: Dict[str, Any],
                      features: Dict[str, Any],
                      sender_info: Optional[Dict[str, Any]] = None,
                      thread_context: Optional[List[Dict[str, Any]]] = None,
                      memory_context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Classify message priority using multi-factor analysis
        """
        try:
            # Prepare inputs
            content_str = self._format_content(content)
            features_str = self._format_features(features)
            sender_str = self._format_sender_info(sender_info)
            thread_str = self._format_thread_context(thread_context)
            memory_str = self._format_memory_context(memory_context)
            
            # Get format instructions
            format_instructions = self.output_parser.get_format_instructions()
            
            # Create prompt
            messages = self.prompt.format_messages(
                content=content_str,
                features=features_str,
                sender_info=sender_str,
                thread_context=thread_str,
                memory_context=memory_str,
                format_instructions=format_instructions
            )
            
            # Get LLM response
            response = await self.llm.ainvoke(messages)
            
            # Parse response
            classification = self.output_parser.parse(response.content)
            
            # Apply rule-based adjustments
            adjusted_classification = await self._apply_rule_adjustments(
                classification, features, sender_info
            )
            
            self.logger.info("Message classified",
                           priority=adjusted_classification.priority_score,
                           importance=adjusted_classification.importance_score,
                           urgency=adjusted_classification.urgency_score)
            
            return adjusted_classification.dict()
            
        except Exception as e:
            self.logger.error("Classification failed", error=str(e))
            
            # Return default classification
            return {
                "priority_score": 0.5,
                "importance_score": 0.5,
                "urgency_score": 0.5,
                "reasoning": f"Classification failed: {str(e)}",
                "key_factors": ["error"],
                "suggested_action": "Manual review required"
            }
    
    def _format_content(self, content: Dict[str, Any]) -> str:
        """Format message content for analysis"""
        parts = []
        
        if subject := content.get("subject"):
            parts.append(f"Subject: {subject}")
            
        if sender := content.get("sender_email"):
            parts.append(f"From: {sender}")
            
        if body := content.get("content"):
            # Truncate long content
            body_preview = body[:1000] + "..." if len(body) > 1000 else body
            parts.append(f"Body: {body_preview}")
            
        if timestamp := content.get("timestamp"):
            parts.append(f"Received: {timestamp}")
            
        return "\n".join(parts)
    
    def _format_features(self, features: Dict[str, Any]) -> str:
        """Format extracted features"""
        feature_lines = []
        
        for key, value in features.items():
            if isinstance(value, bool):
                if value:
                    feature_lines.append(f"- {key.replace('_', ' ').title()}: Yes")
            elif isinstance(value, (int, float)):
                feature_lines.append(f"- {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                feature_lines.append(f"- {key.replace('_', ' ').title()}: {value}")
                
        return "\n".join(feature_lines)
    
    def _format_sender_info(self, sender_info: Optional[Dict[str, Any]]) -> str:
        """Format sender information"""
        if not sender_info:
            return "No sender information available"
            
        lines = []
        
        if email := sender_info.get("email"):
            lines.append(f"Email: {email}")
            
        if name := sender_info.get("display_name"):
            lines.append(f"Name: {name}")
            
        if sender_info.get("is_vip"):
            lines.append("VIP Status: Yes")
            
        if importance := sender_info.get("importance_score"):
            lines.append(f"Historical Importance: {importance:.2f}")
            
        if response_rate := sender_info.get("response_rate"):
            lines.append(f"Response Rate: {response_rate:.1%}")
            
        if tags := sender_info.get("tags"):
            lines.append(f"Tags: {', '.join(tags)}")
            
        return "\n".join(lines) if lines else "Unknown sender"
    
    def _format_thread_context(self, thread_context: Optional[List[Dict[str, Any]]]) -> str:
        """Format thread conversation history"""
        if not thread_context:
            return "No thread context"
            
        lines = [f"Thread has {len(thread_context)} previous messages:"]
        
        # Show last 3 messages
        for msg in thread_context[-3:]:
            sender = msg.get("sender", "Unknown")
            preview = msg.get("content", "")[:100]
            timestamp = msg.get("timestamp", "")
            lines.append(f"- From {sender} at {timestamp}: {preview}...")
            
        return "\n".join(lines)
    
    def _format_memory_context(self, memory_context: Optional[List[Dict[str, Any]]]) -> str:
        """Format relevant memories"""
        if not memory_context:
            return "No relevant memories found"
            
        lines = [f"Found {len(memory_context)} relevant memories:"]
        
        for memory in memory_context[:3]:  # Top 3 memories
            content = memory.get("content", {})
            similarity = memory.get("similarity", 0)
            lines.append(f"- (Similarity: {similarity:.2f}) {str(content)[:100]}...")
            
        return "\n".join(lines)
    
    async def _apply_rule_adjustments(self,
                                    classification: PriorityClassification,
                                    features: Dict[str, Any],
                                    sender_info: Optional[Dict[str, Any]]) -> PriorityClassification:
        """Apply rule-based adjustments to classification"""
        
        # VIP sender boost
        if sender_info and sender_info.get("is_vip"):
            classification.priority_score = min(1.0, classification.priority_score + 0.2)
            classification.importance_score = min(1.0, classification.importance_score + 0.3)
            classification.key_factors.append("VIP sender")
            
        # Deadline detection boost
        if features.get("has_deadline"):
            classification.urgency_score = min(1.0, classification.urgency_score + 0.3)
            classification.priority_score = min(1.0, classification.priority_score + 0.2)
            classification.key_factors.append("Contains deadline")
            
        # Active thread boost
        if features.get("is_thread_active"):
            classification.urgency_score = min(1.0, classification.urgency_score + 0.1)
            classification.key_factors.append("Active conversation thread")
            
        # Low sender importance penalty
        if sender_info and sender_info.get("importance_score", 0.5) < 0.3:
            classification.priority_score = max(0.0, classification.priority_score - 0.2)
            
        # Recalculate overall priority
        classification.priority_score = (
            classification.importance_score * 0.5 + 
            classification.urgency_score * 0.5
        )
        
        return classification


class ImportanceAnalyzer:
    """
    Analyzes long-term importance of messages
    Focuses on business value and relationship importance
    """
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.logger = logger.bind(component="ImportanceAnalyzer")
        
    async def analyze_importance(self,
                               content: Dict[str, Any],
                               sender_profile: Dict[str, Any],
                               historical_context: List[Dict[str, Any]]) -> float:
        """
        Analyze the long-term importance of a message
        Returns score from 0.0 to 1.0
        """
        prompt = f"""
Analyze the long-term importance of this message:

Message: {content.get('subject', 'No subject')}
From: {sender_profile.get('email', 'Unknown')}
Sender Importance: {sender_profile.get('importance_score', 0.5)}
Historical Interactions: {len(historical_context)}

Consider:
1. Business relationship value
2. Strategic importance
3. Knowledge/information value
4. Relationship maintenance needs

Return only a number between 0.0 and 1.0 representing importance.
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))
        except Exception as e:
            self.logger.error("Importance analysis failed", error=str(e))
            return 0.5