"""
Session logging for RAG operations and API calls.
Tracks all LLM calls, embeddings, and retrieved chunks for evaluation and debugging.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import random
import string


class SessionLogger:
    """Logs RAG operations and API calls for a single session."""
    
    def __init__(self, query_title: str, mode: str):
        """
        Initialize a new session logger.
        
        Args:
            query_title: User's query to use as session title
            mode: "paper_brain" or "multi_paper_rag"
        """
        self.session_id = self._generate_session_id()
        self.title = query_title[:100]  # Truncate long titles
        self.mode = mode
        self.timestamp_start = datetime.now().isoformat()
        self.timestamp_end = None
        
        # Storage for logs
        self.rag_chunks: List[Dict[str, Any]] = []
        self.api_calls_embeddings: List[Dict[str, Any]] = []
        self.api_calls_llm: List[Dict[str, Any]] = []
        
        # Counters for IDs
        self._chunk_counter = 0
        self._embedding_counter = 0
        self._llm_counter = 0
        
        # Ensure logs directory exists
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID based on timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return f"session_{timestamp}_{random_suffix}"
    
    def log_rag_chunk(
        self,
        text: str,
        score: float,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        retrieval_method: str = "hybrid_mmr"
    ):
        """
        Log a retrieved RAG chunk.
        
        Args:
            text: Full chunk text
            score: Relevance score
            source: Document source (paper title/ID)
            metadata: Additional metadata (page, section, etc.)
            retrieval_method: Method used for retrieval
        """
        self._chunk_counter += 1
        chunk_log = {
            "chunk_id": f"chunk_{self._chunk_counter:03d}",
            "timestamp": datetime.now().isoformat(),
            "document_source": source,
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "full_text": text,
            "score": round(score, 4) if score is not None else None,
            "retrieval_method": retrieval_method,
            "metadata": metadata or {}
        }
        self.rag_chunks.append(chunk_log)
    
    def log_embedding_call(
        self,
        input_text: str,
        input_type: str = "query",
        model: str = "text-embedding-004",
        input_token_count: Optional[int] = None,
        output_dimensions: int = 768,
        latency_ms: Optional[float] = None
    ):
        """
        Log an embedding API call.
        
        Args:
            input_text: Text being embedded
            input_type: "query" or "document"
            model: Embedding model name
            input_token_count: Number of input tokens
            output_dimensions: Embedding vector dimensions
            latency_ms: API call latency in milliseconds
        """
        self._embedding_counter += 1
        embedding_log = {
            "call_id": f"emb_{self._embedding_counter:03d}",
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_type": input_type,
            "input_text_preview": input_text[:100] + "..." if len(input_text) > 100 else input_text,
            "input_token_count": input_token_count,
            "output_dimensions": output_dimensions,
            "latency_ms": round(latency_ms, 2) if latency_ms else None
        }
        self.api_calls_embeddings.append(embedding_log)
    
    def log_llm_call(
        self,
        call_type: str,
        input_text: str,
        output_text: str,
        model: str = "gemini-2.5-flash-lite",
        prompt_preview: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        latency_ms: Optional[float] = None,
        temperature: float = 0.7
    ):
        """
        Log an LLM API call.
        
        Args:
            call_type: Type of call (semantic_rewrite, intent_routing, agent_reasoning, etc.)
            input_text: Input/query text
            output_text: LLM response
            model: LLM model name
            prompt_preview: Preview of system prompt if relevant
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            latency_ms: API call latency in milliseconds
            temperature: Model temperature setting
        """
        self._llm_counter += 1
        llm_log = {
            "call_id": f"llm_{self._llm_counter:03d}",
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "call_type": call_type,
            "prompt_preview": prompt_preview[:200] + "..." if prompt_preview and len(prompt_preview) > 200 else prompt_preview,
            "input_tokens": input_tokens,
            "input_preview": input_text[:200] + "..." if len(input_text) > 200 else input_text,
            "output_tokens": output_tokens,
            "output_preview": output_text[:200] + "..." if len(output_text) > 200 else output_text,
            "full_output": output_text,
            "latency_ms": round(latency_ms, 2) if latency_ms else None,
            "temperature": temperature
        }
        self.api_calls_llm.append(llm_log)
    
    def save_session(self):
        """Save session logs to JSON file."""
        self.timestamp_end = datetime.now().isoformat()
        
        session_data = {
            "session_id": self.session_id,
            "title": self.title,
            "mode": self.mode,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "rag_chunks": self.rag_chunks,
            "api_calls": {
                "embeddings": self.api_calls_embeddings,
                "llm": self.api_calls_llm
            },
            "summary": {
                "total_rag_chunks": len(self.rag_chunks),
                "total_embedding_calls": len(self.api_calls_embeddings),
                "total_llm_calls": len(self.api_calls_llm),
                "total_input_tokens": sum(log.get("input_tokens", 0) or 0 for log in self.api_calls_llm),
                "total_output_tokens": sum(log.get("output_tokens", 0) or 0 for log in self.api_calls_llm)
            }
        }
        
        file_path = os.path.join(self.logs_dir, f"{self.session_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for current session."""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "mode": self.mode,
            "rag_chunks_count": len(self.rag_chunks),
            "embedding_calls_count": len(self.api_calls_embeddings),
            "llm_calls_count": len(self.api_calls_llm),
            "total_input_tokens": sum(log.get("input_tokens", 0) or 0 for log in self.api_calls_llm),
            "total_output_tokens": sum(log.get("output_tokens", 0) or 0 for log in self.api_calls_llm)
        }
