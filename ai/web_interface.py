"""
Web-Friendly Interface for Paper Brain AI

Wraps CLI functions with JSON responses for FastAPI integration.
Returns structured data instead of printing to console.
"""

from typing import List, Dict, Any, Optional
import asyncio
import time
import requests
import feedparser
import chromadb
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
import os
from .api_config import get_brain_llm, get_chat_llm, QuotaExhaustedError
from .fetcher import ingest_arxiv_paper
from .rag import multi_paper_rag_with_documents
from .logger import SessionLogger


async def web_brain_search(query: str, logger: Optional[SessionLogger] = None) -> Dict[str, Any]:
    """
    Search arXiv papers with semantic rewriting and ranking.
    
    Args:
        query: User's research query
        logger: Optional session logger
        
    Returns:
        {
            "thinking_steps": [
                {"step": "rewriting", "status": "complete", "result": "optimized query"},
                {"step": "searching", "status": "complete", "result": "15 papers found"},
                {"step": "ranking", "status": "complete", "result": "10 papers ranked"}
            ],
            "papers": [
                {
                    "title": "...",
                    "authors": "...",
                    "abstract": "...",
                    "arxiv_id": "...",
                    "url": "...",
                    "score": 0.95
                }
            ],
            "error": None
        }
    """
    thinking_steps = []
    
    try:
        # Step 1: Semantic rewrite
        thinking_steps.append({"step": "rewriting", "status": "in_progress", "result": None})
        
        llm = get_brain_llm(temperature=0.1)
        prompt = f"""You are a research paper search optimizer. Rewrite the user's query into an optimal arXiv search string.

CONSTRAINTS:
- Use technical terms and keywords
- use clean punctutation marks 
- Remove filler words (e.g., "papers about", "research on")
- Focus on core concepts
- Keep domain-specific terminology

USER QUERY: "{query}"

OUTPUT (search string only, no explanation):"""
        
        start_time = time.time()
        response = await llm.acomplete(prompt)
        latency_ms = (time.time() - start_time) * 1000
        
        semantic_query = str(response).strip().strip('"')
        
        # Log LLM call
        if logger:
            logger.log_llm_call(
                call_type="semantic_rewrite",
                input_text=query,
                output_text=semantic_query,
                prompt_preview=prompt,
                latency_ms=latency_ms,
                temperature=0.1
            )
        
        thinking_steps[-1] = {"step": "rewriting", "status": "complete", "result": semantic_query}
        
        # Step 2: Search arXiv
        thinking_steps.append({"step": "searching", "status": "in_progress", "result": None})
        
        base_url = 'http://export.arxiv.org/api/query'
        params = {
            'search_query': f'all:{semantic_query}',
            'start': 0,
            'max_results': 15,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            return {
                "thinking_steps": thinking_steps,
                "papers": [],
                "error": "No papers found. Try a different query."
            }
        
        # Extract paper data
        papers = []
        for entry in feed.entries:
            arxiv_id = entry.id.split('/abs/')[-1]
            papers.append({
                'title': entry.title.replace('\n', ' ').strip(),
                'abstract': entry.summary.replace('\n', ' ').strip(),
                'authors': ', '.join([a.name for a in entry.authors[:3]]),
                'arxiv_id': arxiv_id,
                'url': entry.link
            })
        
        thinking_steps[-1] = {"step": "searching", "status": "complete", "result": f"{len(papers)} papers found"}
        
        # Step 3: Rank by relevance using ChromaDB
        thinking_steps.append({"step": "ranking", "status": "in_progress", "result": None})
        
        client = chromadb.Client()
        google_ef = GoogleGenerativeAiEmbeddingFunction(
            api_key=os.getenv("GOOGLE_API_KEY2"),
            model_name="models/text-embedding-004"
        )
        
        collection_name = f"papers_{int(time.time() * 1000000)}"
        collection = client.create_collection(
            name=collection_name,
            embedding_function=google_ef
        )
        
        # Add abstracts to collection
        for i, paper in enumerate(papers):
            collection.add(
                documents=[paper['abstract']],
                metadatas=[{'index': i}],
                ids=[f"paper_{i}"]
            )
        
        # Query for top 10 matches
        results = collection.query(
            query_texts=[semantic_query],
            n_results=min(10, len(papers))
        )
        
        # Build ranked list
        ranked = []
        for i, doc_id in enumerate(results['ids'][0]):
            idx = results['metadatas'][0][i]['index']
            paper = papers[idx].copy()
            paper['score'] = round(1.0 - results['distances'][0][i], 3)
            ranked.append(paper)
        
        thinking_steps[-1] = {"step": "ranking", "status": "complete", "result": f"{len(ranked)} papers ranked"}
        
        return {
            "thinking_steps": thinking_steps,
            "papers": ranked,
            "error": None
        }
        
    except QuotaExhaustedError as e:
        return {
            "thinking_steps": thinking_steps,
            "papers": [],
            "error": f"quota_exhausted: {e.message}"
        }
    except Exception as e:
        return {
            "thinking_steps": thinking_steps,
            "papers": [],
            "error": f"error: {str(e)}"
        }


async def web_brain_load_papers(paper_ids: List[str], logger: Optional[SessionLogger] = None) -> Dict[str, Any]:
    """
    Load selected papers from arXiv and prepare for RAG.
    
    Args:
        paper_ids: List of arXiv IDs to load
        logger: Optional session logger
        
    Returns:
        {
            "thinking_steps": [
                {"step": "loading", "status": "complete", "result": "3 papers loaded"}
            ],
            "documents": [Document objects],
            "loaded_papers": ["paper_title1", "paper_title2", ...],
            "error": None
        }
    """
    thinking_steps = []
    documents = []
    loaded_papers = []
    
    try:
        thinking_steps.append({"step": "loading", "status": "in_progress", "result": None})
        
        for arxiv_id in paper_ids:
            try:
                # Run in thread pool to avoid blocking event loop
                docs = await asyncio.to_thread(ingest_arxiv_paper, arxiv_id)
                documents.extend(docs)
                # Get paper title from first document's metadata
                if docs and hasattr(docs[0], 'metadata'):
                    loaded_papers.append(docs[0].metadata.get('title', arxiv_id))
                else:
                    loaded_papers.append(arxiv_id)
            except Exception as e:
                print(f"⚠️  Failed to load {arxiv_id}: {e}")
        
        thinking_steps[-1] = {"step": "loading", "status": "complete", "result": f"{len(documents)} documents loaded from {len(loaded_papers)} papers"}
        
        return {
            "thinking_steps": thinking_steps,
            "documents": documents,
            "loaded_papers": loaded_papers,
            "error": None if documents else "Failed to load any papers"
        }
        
    except Exception as e:
        return {
            "thinking_steps": thinking_steps,
            "documents": [],
            "loaded_papers": [],
            "error": f"error: {str(e)}"
        }


async def web_chat_query(query: str, documents: List[Document], logger: Optional[SessionLogger] = None) -> Dict[str, Any]:
    """
    Query loaded papers using RAG with intelligent routing.
    
    Args:
        query: User's question
        documents: Loaded paper documents
        logger: Optional session logger
        
    Returns:
        {
            "thinking_steps": [
                {"step": "routing", "status": "complete", "result": "qa engine selected"},
                {"step": "retrieving", "status": "complete", "result": "5 chunks retrieved"},
                {"step": "generating", "status": "complete", "result": "answer generated"}
            ],
            "answer": "...",
            "citations": [
                {"paper": "Paper Title", "page": 5}
            ],
            "error": None
        }
    """
    thinking_steps = []
    
    try:
        if not documents:
            return {
                "thinking_steps": [],
                "answer": "",
                "citations": [],
                "error": "No papers loaded. Please load papers first."
            }
        
        # Indicate routing
        thinking_steps.append({"step": "routing", "status": "in_progress", "result": None})
        
        # Call RAG function in thread pool to avoid event loop conflicts
        start_time = time.time()
        response = await asyncio.to_thread(multi_paper_rag_with_documents, documents, query, logger)
        latency_ms = (time.time() - start_time) * 1000
        
        thinking_steps[-1] = {"step": "routing", "status": "complete", "result": "query routed"}
        thinking_steps.append({"step": "generating", "status": "complete", "result": "answer generated"})
        
        # Extract citations from response
        import re
        citations_raw = re.findall(r'\[([^,]+), Page (\d+)\]', str(response))
        citations = [{"paper": paper, "page": int(page)} for paper, page in citations_raw]
        unique_citations = list({f"{c['paper']}-{c['page']}": c for c in citations}.values())
        
        return {
            "thinking_steps": thinking_steps,
            "answer": str(response),
            "citations": unique_citations,
            "error": None
        }
        
    except QuotaExhaustedError as e:
        return {
            "thinking_steps": thinking_steps,
            "answer": "",
            "citations": [],
            "error": f"quota_exhausted: {e.message}"
        }
    except Exception as e:
        return {
            "thinking_steps": thinking_steps,
            "answer": "",
            "citations": [],
            "error": f"error: {str(e)}"
        }
