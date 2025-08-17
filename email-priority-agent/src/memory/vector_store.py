"""
Vector Memory Store using Qdrant
Handles embedding storage and similarity search for memory retrieval
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
import asyncio

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    SearchRequest, Filter, FieldCondition, 
    MatchValue, Range
)
from qdrant_client.http import models
import structlog

from ..utils.embeddings import EmbeddingService
from ..utils.config import get_settings

logger = structlog.get_logger()


class VectorMemoryStore:
    """
    Vector-based memory storage and retrieval using Qdrant
    Optimized for semantic search and memory association
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logger.bind(component="VectorMemoryStore")
        self.embedding_service = EmbeddingService()
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            host=self.settings.qdrant_host,
            port=self.settings.qdrant_port,
            api_key=self.settings.qdrant_api_key if self.settings.qdrant_api_key else None
        )
        
        # Collection names
        self.collections = {
            "messages": "email_messages",
            "interactions": "user_interactions",
            "knowledge": "domain_knowledge"
        }
        
        self._initialized = False
        
    async def initialize(self):
        """Initialize vector collections"""
        if self._initialized:
            return
            
        try:
            # Create collections if they don't exist
            for collection_type, collection_name in self.collections.items():
                collection_exists = await self._collection_exists(collection_name)
                
                if not collection_exists:
                    await self._create_collection(collection_name)
                    self.logger.info(f"Created collection: {collection_name}")
                    
            self._initialized = True
            self.logger.info("Vector store initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize vector store", error=str(e))
            raise
    
    async def _collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists"""
        try:
            collections = await asyncio.to_thread(
                self.client.get_collections
            )
            return any(col.name == collection_name for col in collections.collections)
        except Exception:
            return False
    
    async def _create_collection(self, collection_name: str):
        """Create a new collection with appropriate settings"""
        await asyncio.to_thread(
            self.client.create_collection,
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # OpenAI embedding dimension
                distance=Distance.COSINE
            )
        )
    
    async def store_message_embedding(self,
                                    message_id: str,
                                    content: str,
                                    metadata: Dict[str, Any]) -> str:
        """Store message with its embedding"""
        # Generate embedding
        embedding = await self.embedding_service.create_embedding(content)
        
        # Create point
        point_id = str(uuid.uuid4())
        point = PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload={
                "message_id": message_id,
                "content": content[:1000],  # Store preview
                "timestamp": datetime.utcnow().isoformat(),
                **metadata
            }
        )
        
        # Store in Qdrant
        await asyncio.to_thread(
            self.client.upsert,
            collection_name=self.collections["messages"],
            points=[point]
        )
        
        self.logger.info("Stored message embedding",
                        message_id=message_id,
                        point_id=point_id)
        
        return point_id
    
    async def search_similar_memories(self,
                                    query: str,
                                    k: int = 5,
                                    filters: Optional[Dict[str, Any]] = None,
                                    collection: str = "messages") -> List[Dict[str, Any]]:
        """Search for similar memories using vector similarity"""
        # Generate query embedding
        query_embedding = await self.embedding_service.create_embedding(query)
        
        # Build filter conditions
        filter_conditions = []
        if filters:
            for key, value in filters.items():
                if isinstance(value, (str, int, float, bool)):
                    filter_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                elif isinstance(value, dict) and "min" in value and "max" in value:
                    filter_conditions.append(
                        FieldCondition(
                            key=key,
                            range=Range(
                                gte=value["min"],
                                lte=value["max"]
                            )
                        )
                    )
        
        # Prepare search filter
        search_filter = Filter(
            must=filter_conditions
        ) if filter_conditions else None
        
        # Search
        results = await asyncio.to_thread(
            self.client.search,
            collection_name=self.collections.get(collection, "messages"),
            query_vector=query_embedding.tolist(),
            limit=k,
            query_filter=search_filter
        )
        
        # Format results
        memories = []
        for result in results:
            memory = {
                "id": result.id,
                "score": result.score,
                "content": result.payload.get("content", ""),
                "metadata": {
                    k: v for k, v in result.payload.items() 
                    if k not in ["content", "timestamp"]
                },
                "timestamp": result.payload.get("timestamp")
            }
            memories.append(memory)
            
        self.logger.info("Found similar memories",
                        query_preview=query[:50],
                        result_count=len(memories))
        
        return memories
    
    async def get_sender_memories(self,
                                sender_email: str,
                                limit: int = 20) -> List[Dict[str, Any]]:
        """Get all memories related to a specific sender"""
        # Search with sender filter
        results = await asyncio.to_thread(
            self.client.scroll,
            collection_name=self.collections["messages"],
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="sender_email",
                        match=MatchValue(value=sender_email)
                    )
                ]
            ),
            limit=limit,
            order_by="timestamp"
        )
        
        memories = []
        for point in results[0]:  # First element contains points
            memory = {
                "id": point.id,
                "content": point.payload.get("content", ""),
                "timestamp": point.payload.get("timestamp"),
                "message_id": point.payload.get("message_id"),
                "subject": point.payload.get("subject"),
                "importance": point.payload.get("importance_score", 0.5)
            }
            memories.append(memory)
            
        return memories
    
    async def get_thread_memories(self,
                                thread_id: str,
                                limit: int = 50) -> List[Dict[str, Any]]:
        """Get all memories in a conversation thread"""
        results = await asyncio.to_thread(
            self.client.scroll,
            collection_name=self.collections["messages"],
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="thread_id",
                        match=MatchValue(value=thread_id)
                    )
                ]
            ),
            limit=limit,
            order_by="timestamp"
        )
        
        memories = []
        for point in results[0]:
            memory = {
                "id": point.id,
                "content": point.payload.get("content", ""),
                "timestamp": point.payload.get("timestamp"),
                "message_id": point.payload.get("message_id"),
                "sender": point.payload.get("sender_email"),
                "importance": point.payload.get("importance_score", 0.5)
            }
            memories.append(memory)
            
        return sorted(memories, key=lambda x: x["timestamp"])
    
    async def find_related_contexts(self,
                                  embedding: np.ndarray,
                                  k: int = 10,
                                  threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find contexts related to a given embedding"""
        # Search across all collections
        all_results = []
        
        for collection_name in self.collections.values():
            try:
                results = await asyncio.to_thread(
                    self.client.search,
                    collection_name=collection_name,
                    query_vector=embedding.tolist(),
                    limit=k,
                    score_threshold=threshold
                )
                
                for result in results:
                    all_results.append({
                        "collection": collection_name,
                        "id": result.id,
                        "score": result.score,
                        "payload": result.payload
                    })
            except Exception as e:
                self.logger.warning(f"Search failed for {collection_name}", 
                                  error=str(e))
                
        # Sort by score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        return all_results[:k]
    
    async def update_memory_importance(self,
                                     memory_id: str,
                                     importance_delta: float,
                                     collection: str = "messages"):
        """Update the importance score of a memory"""
        try:
            # Get current point
            points = await asyncio.to_thread(
                self.client.retrieve,
                collection_name=self.collections.get(collection, "messages"),
                ids=[memory_id]
            )
            
            if points:
                point = points[0]
                current_importance = point.payload.get("importance_score", 0.5)
                new_importance = max(0.0, min(1.0, current_importance + importance_delta))
                
                # Update payload
                await asyncio.to_thread(
                    self.client.set_payload,
                    collection_name=self.collections.get(collection, "messages"),
                    payload={
                        "importance_score": new_importance,
                        "last_updated": datetime.utcnow().isoformat()
                    },
                    points=[memory_id]
                )
                
                self.logger.info("Updated memory importance",
                               memory_id=memory_id,
                               old_importance=current_importance,
                               new_importance=new_importance)
                
        except Exception as e:
            self.logger.error("Failed to update memory importance",
                            memory_id=memory_id,
                            error=str(e))
    
    async def create_knowledge_graph_connections(self,
                                               source_id: str,
                                               target_ids: List[str],
                                               connection_type: str,
                                               strength: float = 1.0):
        """Create connections between memories for knowledge graph"""
        try:
            # Update source memory with connections
            connections = []
            for target_id in target_ids:
                connections.append({
                    "target_id": target_id,
                    "type": connection_type,
                    "strength": strength,
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # Get existing connections
            points = await asyncio.to_thread(
                self.client.retrieve,
                collection_name=self.collections["messages"],
                ids=[source_id]
            )
            
            if points:
                existing_connections = points[0].payload.get("connections", [])
                existing_connections.extend(connections)
                
                # Update with new connections
                await asyncio.to_thread(
                    self.client.set_payload,
                    collection_name=self.collections["messages"],
                    payload={
                        "connections": existing_connections
                    },
                    points=[source_id]
                )
                
                self.logger.info("Created knowledge graph connections",
                               source_id=source_id,
                               target_count=len(target_ids),
                               connection_type=connection_type)
                
        except Exception as e:
            self.logger.error("Failed to create connections",
                            source_id=source_id,
                            error=str(e))
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        stats = {}
        
        for collection_type, collection_name in self.collections.items():
            try:
                info = await asyncio.to_thread(
                    self.client.get_collection,
                    collection_name=collection_name
                )
                
                stats[collection_type] = {
                    "count": info.vectors_count,
                    "indexed": info.indexed_vectors_count,
                    "status": info.status
                }
            except Exception as e:
                stats[collection_type] = {
                    "error": str(e)
                }
                
        return stats