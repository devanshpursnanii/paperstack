"""
FastAPI Backend for Paper Brain AI

5 Endpoints:
1. POST /session/create - Create new session
2. POST /brain/search - Search papers with Paper Brain
3. POST /brain/load - Load selected papers
4. POST /chat/message - Send message to Paper Chat
5. GET /session/{session_id}/info - Get session info and logs
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import (
    CreateSessionRequest, CreateSessionResponse,
    BrainSearchRequest, BrainSearchResponse,
    BrainLoadRequest, BrainLoadResponse,
    ChatMessageRequest, ChatMessageResponse,
    SessionInfoResponse, ErrorResponse,
    ThinkingStep, Paper, Citation, QuotaStatus, SessionInfo
)
from backend.session import (
    create_session, get_session, cleanup_old_sessions,
    get_session_count
)
from ai.web_interface import web_brain_search, web_brain_load_papers, web_chat_query
from ai.api_config import QuotaExhaustedError


# ==================
# FASTAPI APP SETUP
# ==================

app = FastAPI(
    title="Paper Brain AI API",
    description="Research paper discovery and RAG chat API",
    version="1.0.0"
)

# CORS Configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://192.168.0.106:3000",
        "http://192.168.0.107:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# ==================
# ENDPOINTS
# ==================

@app.post("/session/create", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_session(request: CreateSessionRequest):
    """
    Create a new session for Paper Brain.
    
    - **initial_query**: User's research query for session title
    
    Returns session_id and creation timestamp.
    """
    try:
        session = create_session(initial_query=request.initial_query)
        
        return CreateSessionResponse(
            session_id=session.session_id,
            created_at=session.created_at.isoformat(),
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@app.post("/brain/search", response_model=BrainSearchResponse)
async def brain_search(request: BrainSearchRequest):
    """
    Search arXiv papers with Paper Brain.
    
    - **session_id**: Active session UUID
    - **query**: Research query to search
    
    Returns thinking steps, ranked papers, and remaining searches.
    """
    # Get session
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check quota
    can_use, cooldown_mins = session.quota.can_use_brain()
    if not can_use:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "quota_exhausted",
                "cooldown_minutes": cooldown_mins,
                "message": f"Paper Brain quota exhausted. Try again in {cooldown_mins} minutes."
            }
        )
    
    # Perform search
    try:
        result = await web_brain_search(request.query, search_mode=request.search_mode, logger=session.logger)
        
        # Check for errors
        if result.get("error"):
            if "quota_exhausted" in result["error"]:
                # Mark API as exhausted
                session.quota.mark_api_exhausted()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "api_quota_exhausted",
                        "cooldown_minutes": 30,
                        "message": "API quota exhausted. Try again in 30 minutes."
                    }
                )
            else:
                return BrainSearchResponse(
                    thinking_steps=[ThinkingStep(**step) for step in result["thinking_steps"]],
                    papers=[],
                    searches_remaining=session.quota.get_remaining_brain_searches(),
                    error=result["error"]
                )
        
        # Increment quota
        session.quota.increment_brain()
        
        # Add to history
        session.brain_history.append({
            "query": request.query,
            "papers_found": len(result["papers"]),
            "timestamp": datetime.now().isoformat()
        })
        
        return BrainSearchResponse(
            thinking_steps=[ThinkingStep(**step) for step in result["thinking_steps"]],
            papers=[Paper(**paper) for paper in result["papers"]],
            searches_remaining=session.quota.get_remaining_brain_searches(),
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return BrainSearchResponse(
            thinking_steps=[],
            papers=[],
            searches_remaining=session.quota.get_remaining_brain_searches(),
            error=f"Internal error: {str(e)}"
        )


@app.post("/brain/load", response_model=BrainLoadResponse)
async def brain_load(request: BrainLoadRequest):
    """
    Load selected papers for RAG.
    
    - **session_id**: Active session UUID
    - **paper_ids**: List of arXiv IDs to load
    
    Returns loading status and paper titles.
    """
    # Get session
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Load papers
    try:
        # Add initial status
        thinking_steps = [
            {"step_number": 1, "description": f"Downloading {len(request.paper_ids)} papers from arXiv..."},
            {"step_number": 2, "description": "Extracting text and building index..."},
        ]
        
        result = await web_brain_load_papers(request.paper_ids, logger=session.logger)
        
        if result.get("error"):
            return BrainLoadResponse(
                thinking_steps=[ThinkingStep(**step) for step in result["thinking_steps"]],
                loaded_papers=[],
                status="failed",
                error=result["error"]
            )
        
        # Store documents in session
        session.loaded_documents = result["documents"]
        session.loaded_paper_titles = result["loaded_papers"]
        session.logger.mode = "multi_paper_rag"  # Switch to RAG mode
        
        return BrainLoadResponse(
            thinking_steps=[ThinkingStep(**step) for step in result["thinking_steps"]],
            loaded_papers=result["loaded_papers"],
            status="success",
            error=None
        )
        
    except Exception as e:
        return BrainLoadResponse(
            thinking_steps=[],
            loaded_papers=[],
            status="failed",
            error=f"Internal error: {str(e)}"
        )


@app.post("/chat/message", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest):
    """
    Send a message to Paper Chat.
    
    - **session_id**: Active session UUID
    - **message**: User's question about loaded papers
    
    Returns answer with citations and remaining messages.
    """
    # Get session
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if papers loaded
    if not session.loaded_documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No papers loaded. Please load papers first using /brain/load"
        )
    
    # Check quota
    can_use, cooldown_mins = session.quota.can_use_chat()
    if not can_use:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "quota_exhausted",
                "cooldown_minutes": cooldown_mins,
                "message": f"Paper Chat quota exhausted. Try again in {cooldown_mins} minutes."
            }
        )
    
    # Query RAG
    try:
        result = await web_chat_query(
            request.message,
            session.loaded_documents,
            logger=session.logger
        )
        
        # Check for errors
        if result.get("error"):
            if "quota_exhausted" in result["error"]:
                # Mark API as exhausted
                session.quota.mark_api_exhausted()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "api_quota_exhausted",
                        "cooldown_minutes": 30,
                        "message": "API quota exhausted. Try again in 30 minutes."
                    }
                )
            else:
                return ChatMessageResponse(
                    thinking_steps=[ThinkingStep(**step) for step in result["thinking_steps"]],
                    answer="",
                    citations=[],
                    messages_remaining=session.quota.get_remaining_chat_messages(),
                    error=result["error"]
                )
        
        # Increment quota
        session.quota.increment_chat()
        
        # Add to history
        session.chat_history.append({
            "message": request.message,
            "answer": result["answer"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Strip markdown formatting
        clean_answer = result["answer"].replace("**", "")
        
        return ChatMessageResponse(
            thinking_steps=[ThinkingStep(**step) for step in result["thinking_steps"]],
            answer=clean_answer,
            citations=[Citation(**cite) for cite in result["citations"]],
            messages_remaining=session.quota.get_remaining_chat_messages(),
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ChatMessageResponse(
            thinking_steps=[],
            answer="",
            citations=[],
            messages_remaining=session.quota.get_remaining_chat_messages(),
            error=f"Internal error: {str(e)}"
        )


@app.get("/session/{session_id}/info", response_model=SessionInfoResponse)
async def get_session_info(session_id: str):
    """
    Get session information, quota status, and logs.
    
    - **session_id**: Session UUID
    
    Returns session metadata, quota status, logs summary, and detailed logs.
    """
    # Get session
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    try:
        # Get quota status
        quota_status_dict = session.quota.get_status()
        quota_status = QuotaStatus(**quota_status_dict)
        
        # Build session info
        session_info = SessionInfo(
            session_id=session.session_id,
            created_at=session.created_at.isoformat(),
            last_activity=session.last_activity.isoformat(),
            initial_query=session.initial_query,
            loaded_papers=session.loaded_paper_titles,
            quota_status=quota_status,
            brain_searches_used=session.quota.brain_searches,
            chat_messages_used=session.quota.chat_messages
        )
        
        # Get logs summary and detailed logs
        logs_summary = session.logger.get_summary()
        
        # Return with detailed logs for dashboard
        return {
            "session_info": session_info,
            "logs_summary": logs_summary,
            "llm_calls": session.logger.api_calls_llm,
            "rag_chunks": session.logger.rag_chunks,
            "error": None
        }
        
    except Exception as e:
        return SessionInfoResponse(
            session_info=SessionInfo(
                session_id=session_id,
                created_at="",
                last_activity="",
                initial_query="",
                loaded_papers=[],
                quota_status=QuotaStatus(brain={}, chat={}, api_exhausted=False),
                brain_searches_used=0,
                chat_messages_used=0
            ),
            logs_summary={},
            error=f"Internal error: {str(e)}"
        )


# ==================
# HEALTH & UTILITY
# ==================

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Paper Brain AI API",
        "version": "1.0.0",
        "status": "running",
        "active_sessions": get_session_count(),
        "endpoints": {
            "create_session": "POST /session/create",
            "brain_search": "POST /brain/search",
            "brain_load": "POST /brain/load",
            "chat_message": "POST /chat/message",
            "session_info": "GET /session/{session_id}/info"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_sessions": get_session_count()
    }


# Cleanup old sessions on startup
@app.on_event("startup")
async def startup_event():
    """Run cleanup on startup - only remove very old sessions.""" 
    deleted = cleanup_old_sessions(max_age_hours=48)  # Changed from 24 to 48 hours
    print(f"✓ FastAPI started. Cleaned up {deleted} old sessions.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
