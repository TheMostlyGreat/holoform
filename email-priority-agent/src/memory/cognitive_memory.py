"""
Cognitive Memory System for Email Priority Agent
Implements multi-tiered memory architecture inspired by A-MEM and CAIM
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
import json
from collections import deque, defaultdict
import uuid

import numpy as np
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from .memory_models import (
    WorkingMemory, ShortTermMemory, LongTermMemory, 
    EpisodicMemory, SenderProfile, ThreadHistory
)
from ..utils.database import get_db_session
from ..utils.embeddings import EmbeddingService

logger = structlog.get_logger()


@dataclass
class MemoryNode:
    """Represents a single memory node in the network"""
    id: str
    content: Dict[str, Any]
    embedding: Optional[np.ndarray]
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    importance_score: float = 0.5
    decay_rate: float = 0.1
    connections: List[Tuple[str, float]] = field(default_factory=list)  # (node_id, strength)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryController:
    """Controls memory operations and transitions between memory tiers"""
    
    def __init__(self, 
                 working_memory_size: int = 20,
                 short_term_size: int = 100,
                 consolidation_interval: int = 300):  # 5 minutes
        self.working_memory_size = working_memory_size
        self.short_term_size = short_term_size
        self.consolidation_interval = consolidation_interval
        self.last_consolidation = datetime.utcnow()
        
    async def should_consolidate(self) -> bool:
        """Check if memory consolidation should occur"""
        time_since_last = (datetime.utcnow() - self.last_consolidation).seconds
        return time_since_last >= self.consolidation_interval
    
    async def consolidate_memories(self, 
                                 working: List[MemoryNode],
                                 short_term: List[MemoryNode]) -> Tuple[List[MemoryNode], List[str]]:
        """
        Consolidate memories from working to short-term and short-term to long-term
        Returns: (memories_to_persist, ids_to_remove)
        """
        # Sort by importance and recency
        working_sorted = sorted(
            working, 
            key=lambda m: (m.importance_score * 0.7 + 
                         (1.0 / (1 + (datetime.utcnow() - m.timestamp).seconds / 3600)) * 0.3),
            reverse=True
        )
        
        # Keep top memories in working, move others to short-term
        to_short_term = working_sorted[self.working_memory_size:]
        
        # Process short-term memories
        all_short_term = short_term + to_short_term
        short_term_sorted = sorted(
            all_short_term,
            key=lambda m: m.importance_score * (1 - m.decay_rate),
            reverse=True
        )
        
        # Identify memories to persist to long-term
        to_persist = []
        to_remove = []
        
        for memory in short_term_sorted[self.short_term_size:]:
            if memory.importance_score > 0.7 or memory.access_count > 5:
                to_persist.append(memory)
            else:
                to_remove.append(memory.id)
                
        self.last_consolidation = datetime.utcnow()
        return to_persist, to_remove


class CognitiveMemorySystem:
    """
    Advanced memory system with cognitive-inspired architecture
    Implements working, short-term, long-term, and episodic memory
    """
    
    def __init__(self):
        self.logger = logger.bind(component="CognitiveMemorySystem")
        self.embedding_service = EmbeddingService()
        self.memory_controller = MemoryController()
        
        # In-memory stores for fast access
        self.working_memory: deque[MemoryNode] = deque(maxlen=20)
        self.short_term_memory: Dict[str, MemoryNode] = {}
        self.memory_graph: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        
        # Start background consolidation task
        self._consolidation_task = None
        
    async def initialize(self):
        """Initialize the memory system"""
        self._consolidation_task = asyncio.create_task(self._consolidation_loop())
        self.logger.info("Cognitive memory system initialized")
        
    async def shutdown(self):
        """Shutdown the memory system"""
        if self._consolidation_task:
            self._consolidation_task.cancel()
            
    async def _consolidation_loop(self):
        """Background task for memory consolidation"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                if await self.memory_controller.should_consolidate():
                    await self._consolidate_memories()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Consolidation error", error=str(e))
                
    async def _consolidate_memories(self):
        """Consolidate memories across tiers"""
        working_list = list(self.working_memory)
        short_term_list = list(self.short_term_memory.values())
        
        to_persist, to_remove = await self.memory_controller.consolidate_memories(
            working_list, short_term_list
        )
        
        # Persist to long-term storage
        async with get_db_session() as session:
            for memory in to_persist:
                await self._persist_to_long_term(session, memory)
                
            # Remove from short-term
            for memory_id in to_remove:
                self.short_term_memory.pop(memory_id, None)
                
            await session.commit()
            
        self.logger.info("Memory consolidation completed",
                        persisted=len(to_persist),
                        removed=len(to_remove))
    
    async def store_interaction(self,
                              message_id: str,
                              content: Dict[str, Any],
                              importance: float = 0.5) -> MemoryNode:
        """Store a new interaction in working memory"""
        # Create embedding
        text_content = f"{content.get('subject', '')} {content.get('content', '')}"
        embedding = await self.embedding_service.create_embedding(text_content)
        
        # Create memory node
        node = MemoryNode(
            id=f"mem_{message_id}",
            content=content,
            embedding=embedding,
            timestamp=datetime.utcnow(),
            importance_score=importance,
            metadata={
                "message_id": message_id,
                "sender": content.get("sender_email"),
                "type": "interaction"
            }
        )
        
        # Add to working memory
        self.working_memory.append(node)
        
        # Update connections based on similarity
        await self._update_memory_connections(node)
        
        self.logger.info("Stored interaction in memory",
                        memory_id=node.id,
                        importance=importance)
        
        return node
    
    async def _update_memory_connections(self, new_node: MemoryNode):
        """Update connections between memory nodes based on similarity"""
        if new_node.embedding is None:
            return
            
        # Check similarity with existing memories
        all_memories = list(self.working_memory) + list(self.short_term_memory.values())
        
        for memory in all_memories:
            if memory.id == new_node.id or memory.embedding is None:
                continue
                
            # Calculate cosine similarity
            similarity = np.dot(new_node.embedding, memory.embedding) / (
                np.linalg.norm(new_node.embedding) * np.linalg.norm(memory.embedding)
            )
            
            if similarity > 0.7:  # Threshold for connection
                # Add bidirectional connection
                new_node.connections.append((memory.id, similarity))
                memory.connections.append((new_node.id, similarity))
                self.memory_graph[new_node.id].append((memory.id, similarity))
                self.memory_graph[memory.id].append((new_node.id, similarity))
    
    async def retrieve_relevant_memories(self,
                                       query: str,
                                       k: int = 5,
                                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to the query using activation spreading"""
        # Create query embedding
        query_embedding = await self.embedding_service.create_embedding(query)
        
        # Search across all memory tiers
        candidates = []
        
        # Working memory
        for node in self.working_memory:
            if node.embedding is not None:
                similarity = np.dot(query_embedding, node.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(node.embedding)
                )
                candidates.append((node, similarity))
        
        # Short-term memory
        for node in self.short_term_memory.values():
            if node.embedding is not None:
                similarity = np.dot(query_embedding, node.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(node.embedding)
                )
                candidates.append((node, similarity))
        
        # Long-term memory (from database)
        async with get_db_session() as session:
            # This would use vector similarity search in production
            stmt = select(LongTermMemory).limit(50)
            result = await session.execute(stmt)
            long_term_memories = result.scalars().all()
            
            for ltm in long_term_memories:
                if ltm.embedding:
                    embedding = np.frombuffer(ltm.embedding, dtype=np.float32)
                    similarity = np.dot(query_embedding, embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
                    )
                    node = MemoryNode(
                        id=ltm.id,
                        content=ltm.content,
                        embedding=embedding,
                        timestamp=ltm.created_at,
                        importance_score=ltm.importance_score,
                        access_count=ltm.access_count
                    )
                    candidates.append((node, similarity))
        
        # Sort by similarity and apply activation spreading
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates[:k*2]  # Get more for spreading activation
        
        # Apply spreading activation
        activated_memories = await self._spreading_activation(
            [c[0] for c in top_candidates],
            [c[1] for c in top_candidates]
        )
        
        # Update access counts and last accessed
        for memory, _ in activated_memories[:k]:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()
        
        # Return top k results
        return [
            {
                "content": memory.content,
                "similarity": score,
                "timestamp": memory.timestamp,
                "importance": memory.importance_score,
                "metadata": memory.metadata
            }
            for memory, score in activated_memories[:k]
        ]
    
    async def _spreading_activation(self,
                                  seed_memories: List[MemoryNode],
                                  initial_activations: List[float],
                                  decay_factor: float = 0.7) -> List[Tuple[MemoryNode, float]]:
        """
        Apply spreading activation to find related memories
        """
        activation_scores = {}
        visited = set()
        
        # Initialize with seed memories
        for memory, activation in zip(seed_memories, initial_activations):
            activation_scores[memory.id] = activation
            
        # Spread activation through connections
        queue = [(m, a) for m, a in zip(seed_memories, initial_activations)]
        
        while queue:
            current_memory, current_activation = queue.pop(0)
            
            if current_memory.id in visited:
                continue
                
            visited.add(current_memory.id)
            
            # Spread to connected memories
            for connected_id, connection_strength in current_memory.connections:
                spread_activation = current_activation * connection_strength * decay_factor
                
                if spread_activation > 0.1:  # Threshold
                    if connected_id in activation_scores:
                        activation_scores[connected_id] = max(
                            activation_scores[connected_id], 
                            spread_activation
                        )
                    else:
                        activation_scores[connected_id] = spread_activation
                        
                        # Add connected memory to queue if in short-term
                        if connected_id in self.short_term_memory:
                            queue.append((
                                self.short_term_memory[connected_id],
                                spread_activation
                            ))
        
        # Combine all activated memories with scores
        result = []
        memory_map = {m.id: m for m in seed_memories}
        memory_map.update(self.short_term_memory)
        
        for memory_id, score in activation_scores.items():
            if memory_id in memory_map:
                result.append((memory_map[memory_id], score))
                
        result.sort(key=lambda x: x[1], reverse=True)
        return result
    
    async def get_sender_profile(self, sender_email: str) -> Dict[str, Any]:
        """Retrieve comprehensive sender profile"""
        async with get_db_session() as session:
            # Get or create sender profile
            stmt = select(SenderProfile).where(SenderProfile.email == sender_email)
            result = await session.execute(stmt)
            profile = result.scalar_one_or_none()
            
            if not profile:
                # Create new profile
                profile = SenderProfile(
                    id=str(uuid.uuid4()),
                    email=sender_email,
                    display_name=sender_email.split('@')[0],
                    importance_score=0.5,
                    total_messages=0,
                    response_rate=0.0,
                    avg_response_time_hours=24.0,
                    is_vip=False,
                    tags=[],
                    metadata={}
                )
                session.add(profile)
                await session.commit()
            
            # Get recent interaction patterns
            recent_memories = await self.retrieve_relevant_memories(
                f"sender:{sender_email}",
                k=10,
                filters={"sender": sender_email}
            )
            
            return {
                "email": profile.email,
                "display_name": profile.display_name,
                "importance_score": profile.importance_score,
                "is_vip": profile.is_vip,
                "total_messages": profile.total_messages,
                "response_rate": profile.response_rate,
                "avg_response_time_hours": profile.avg_response_time_hours,
                "tags": profile.tags,
                "recent_interactions": recent_memories,
                "last_updated": profile.updated_at
            }
    
    async def get_thread_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """Retrieve thread conversation history"""
        async with get_db_session() as session:
            stmt = select(ThreadHistory).where(
                ThreadHistory.thread_id == thread_id
            ).order_by(ThreadHistory.timestamp)
            
            result = await session.execute(stmt)
            messages = result.scalars().all()
            
            return [
                {
                    "message_id": msg.message_id,
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "importance": msg.importance_score
                }
                for msg in messages
            ]
    
    async def store_priority_decision(self,
                                    message_id: str,
                                    decision: Any,
                                    scores: Dict[str, float],
                                    reasoning: str):
        """Store priority decision for learning"""
        async with get_db_session() as session:
            # Store as episodic memory
            episodic = EpisodicMemory(
                id=str(uuid.uuid4()),
                event_type="priority_decision",
                event_data={
                    "message_id": message_id,
                    "decision": decision.value if hasattr(decision, 'value') else str(decision),
                    "scores": scores,
                    "reasoning": reasoning
                },
                timestamp=datetime.utcnow(),
                context={
                    "model_version": "1.0",
                    "features_used": list(scores.keys())
                }
            )
            session.add(episodic)
            await session.commit()
            
        self.logger.info("Stored priority decision",
                        message_id=message_id,
                        decision=str(decision))
    
    async def _persist_to_long_term(self, session: AsyncSession, memory: MemoryNode):
        """Persist memory node to long-term storage"""
        ltm = LongTermMemory(
            id=memory.id,
            content=memory.content,
            embedding=memory.embedding.tobytes() if memory.embedding is not None else None,
            importance_score=memory.importance_score,
            access_count=memory.access_count,
            last_accessed=memory.last_accessed,
            created_at=memory.timestamp,
            metadata=memory.metadata
        )
        session.add(ltm)
        
        # Also update sender profile if applicable
        if sender_email := memory.metadata.get("sender"):
            stmt = select(SenderProfile).where(SenderProfile.email == sender_email)
            result = await session.execute(stmt)
            profile = result.scalar_one_or_none()
            
            if profile:
                profile.total_messages += 1
                profile.last_interaction = datetime.utcnow()
                # Update importance based on interaction patterns
                profile.importance_score = min(
                    1.0,
                    profile.importance_score + 0.01
                )