"""
Titans Memory Adapter for Metis Agent Integration

This module provides an adapter to integrate the Titans-inspired memory system
with the Metis Agent architecture.
"""

import os
import time
from typing import Dict, Any, List, Optional, Union
from .titans_memory import TitansInspiredMemory

class TitansMemoryAdapter:
    """
    Adapter to integrate Titans memory with Metis Agent
    """
    
    def __init__(self, agent, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter
        
        Args:
            agent: Agent instance
            config: Configuration dict with optional parameters
        """
        self.agent = agent
        self.config = config or {}
        
        # Initialize Titans memory with configuration
        memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "titans")
        os.makedirs(memory_dir, exist_ok=True)
        
        self.titans_memory = TitansInspiredMemory(
            memory_dir=memory_dir,
            embedding_dim=self.config.get("embedding_dim", 128),
            surprise_threshold=self.config.get("surprise_threshold", 0.7),
            chunk_size=self.config.get("chunk_size", 3),
            short_term_capacity=self.config.get("short_term_capacity", 15),
            long_term_capacity=self.config.get("long_term_capacity", 1000)
        )
        
        # Load existing state
        self.titans_memory.load_state()
        
        # Track performance metrics
        self.performance_metrics = {
            "queries_processed": 0,
            "memories_stored": 0,
            "adaptations_triggered": 0,
            "average_surprise": 0.0
        }
        
        print("+ Titans memory adapter initialized")
    
    def enhance_query_processing(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced query processing with comprehensive error handling
        
        Args:
            query: User query
            session_id: Session identifier
            
        Returns:
            Enhanced query data
        """
        try:
            # Store the incoming query
            context = f"session_{session_id}" if session_id else "default_session"
            
            storage_info = self.titans_memory.store_memory(
                content=query,
                context=context,
                metadata={
                    "type": "user_query",
                    "session_id": session_id,
                    "timestamp": time.time()
                }
            )
            
            # Get relevant memories for context enhancement
            relevant_memories = self.titans_memory.retrieve_relevant_memories(query, max_results=3)
            
            # Get attention context
            attention_context = self.titans_memory.get_attention_context(query)
            
            # Update performance metrics safely
            self._update_metrics_safely(storage_info)
            
            return {
                "original_query": query,
                "enhanced_context": self._build_memory_context(relevant_memories),
                "storage_info": storage_info,
                "relevant_memories": relevant_memories,
                "attention_metadata": {
                    "num_contexts": attention_context.get("num_contexts", 0),
                    "context_sources": attention_context.get("context_sources", [])
                }
            }
            
        except Exception as e:
            print(f"⚠️ Error in Titans memory enhancement: {e}")
            # Return safe fallback
            return {
                "original_query": query,
                "enhanced_context": "",
                "storage_info": {"stored": False, "error": str(e)},
                "relevant_memories": [],
                "attention_metadata": {"num_contexts": 0, "context_sources": []}
            }
            
    def _update_metrics_safely(self, storage_info: Dict[str, Any]) -> None:
        """
        Safely update performance metrics
        
        Args:
            storage_info: Storage information from store_memory
        """
        try:
            self.performance_metrics["queries_processed"] += 1
            if storage_info.get("stored_long_term"):
                self.performance_metrics["memories_stored"] += 1
            if storage_info.get("triggered_adaptation"):
                self.performance_metrics["adaptations_triggered"] += 1
            
            # Calculate running average surprise safely
            total_queries = self.performance_metrics["queries_processed"]
            current_avg = self.performance_metrics.get("average_surprise", 0.0)
            new_surprise = storage_info.get("surprise_score", 0.0)
            
            if total_queries > 0:
                self.performance_metrics["average_surprise"] = (
                    (current_avg * (total_queries - 1) + new_surprise) / total_queries
                )
        except Exception as e:
            print(f"⚠️ Error updating metrics: {e}")
    
    def store_response(self, query: str, response: Any, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Store agent response in Titans memory with error handling
        
        Args:
            query: User query
            response: Agent response
            session_id: Session identifier
            
        Returns:
            Storage info
        """
        try:
            if not response:
                return {"stored": False, "reason": "empty_response"}
            
            # Extract content from different response formats
            content = ""
            if isinstance(response, dict):
                if "content" in response:
                    content = str(response["content"])
                elif "summary" in response:
                    content = str(response["summary"])
                elif "answer" in response:
                    content = str(response["answer"])
                else:
                    content = str(response)
            else:
                content = str(response)
            
            if not content.strip():
                return {"stored": False, "reason": "empty_content"}
                
            context = f"response_to_session_{session_id}" if session_id else "response_context"
            
            storage_info = self.titans_memory.store_memory(
                content=content,
                context=context,
                metadata={
                    "type": "agent_response",
                    "original_query": query,
                    "session_id": session_id,
                    "timestamp": time.time()
                }
            )
            
            return storage_info
            
        except Exception as e:
            print(f"⚠️ Error storing response in Titans memory: {e}")
            return {"stored": False, "error": str(e)}
    
    def _build_memory_context(self, relevant_memories: List[Dict[str, Any]]) -> str:
        """
        Build enhanced context string from relevant memories
        
        Args:
            relevant_memories: List of relevant memory entries
            
        Returns:
            Context string
        """
        if not relevant_memories:
            return ""
        
        context_parts = ["Previous relevant context:"]
        
        for i, memory in enumerate(relevant_memories, 1):
            relevance = memory["relevance_score"]
            content = memory["content"]
            memory_type = memory["memory_type"]
            
            # Format memory entry
            context_parts.append(
                f"{i}. [{memory_type}] {content} (relevance: {relevance:.2f})"
            )
        
        return "\n".join(context_parts) + "\n"
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive insights about adaptive memory performance
        
        Returns:
            Dictionary with insights
        """
        memory_stats = self.titans_memory.get_memory_stats()
        
        insights = {
            "performance_metrics": self.performance_metrics.copy(),
            "memory_statistics": memory_stats,
            "health_indicators": {
                "memory_utilization": memory_stats["short_term_count"] / self.titans_memory.short_term_memory.maxlen,
                "adaptation_rate": memory_stats["adaptation_count"] / max(1, self.performance_metrics["queries_processed"]),
                "surprise_level": "high" if self.performance_metrics["average_surprise"] > self.titans_memory.surprise_threshold else "normal",
                "learning_active": memory_stats["adaptation_count"] > 0
            },
            "recommendations": self._generate_recommendations(memory_stats)
        }
        
        return insights
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on memory performance
        
        Args:
            stats: Memory statistics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if stats["adaptation_count"] == 0:
            recommendations.append("Consider lowering surprise_threshold to enable more learning")
        
        if stats["avg_surprise_recent"] > 1.5:
            recommendations.append("High surprise levels detected - agent is encountering novel content")
        
        if stats["short_term_count"] < 5:
            recommendations.append("Low short-term memory usage - increase interaction frequency")
        
        if stats["long_term_count"] > 800:
            recommendations.append("Long-term memory approaching capacity - consider periodic cleanup")
        
        return recommendations
    
    def save_state(self) -> None:
        """Save the adaptive memory state"""
        self.titans_memory.save_state()
    
    def configure(self, **kwargs) -> None:
        """
        Dynamically configure the memory system
        
        Available options:
        - surprise_threshold: float (0.1 to 2.0)
        - chunk_size: int (1 to 10)
        """
        if "surprise_threshold" in kwargs:
            threshold = max(0.1, min(2.0, float(kwargs["surprise_threshold"])))
            self.titans_memory.surprise_threshold = threshold
            print(f"🎛️ Updated surprise threshold to {threshold}")
        
        if "chunk_size" in kwargs:
            chunk_size = max(1, min(10, int(kwargs["chunk_size"])))
            self.titans_memory.chunk_size = chunk_size
            print(f"🎛️ Updated chunk size to {chunk_size}")