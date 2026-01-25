-- PostgreSQL Schema for PaperStack Metrics
-- Compatible with Supabase

-- Sessions table: Tracks user sessions
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    session_start_ts TIMESTAMP DEFAULT NOW()
);

-- Requests table: Tracks each chat request with metrics
CREATE TABLE IF NOT EXISTS requests (
    request_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    total_chunk_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    llm_latency_ms DOUBLE PRECISION NOT NULL,
    total_latency_ms DOUBLE PRECISION NOT NULL,
    operation_type TEXT DEFAULT 'chat_message',
    status TEXT DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chunks table: Tracks individual RAG chunks retrieved for each request
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id SERIAL PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES requests(request_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    paper_title TEXT NOT NULL,
    content_preview TEXT NOT NULL,
    chunk_token_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_requests_session ON requests(session_id);
CREATE INDEX IF NOT EXISTS idx_requests_created ON requests(created_at);
CREATE INDEX IF NOT EXISTS idx_chunks_request ON chunks(request_id);

-- Comments for documentation
COMMENT ON TABLE sessions IS 'Tracks user sessions for metrics aggregation';
COMMENT ON TABLE requests IS 'Stores chat request metrics including tokens and latencies';
COMMENT ON TABLE chunks IS 'Stores individual RAG chunks retrieved per request';
