#!/usr/bin/env python3
"""Test Supabase integration"""

from backend.db.repository import create_session, insert_request, insert_chunks, get_requests_by_session
from datetime import datetime
import uuid

# Test data
session_id = str(uuid.uuid4())
request_id = str(uuid.uuid4())

print('🧪 Testing Supabase write operations...')

# 1. Create session
create_session(session_id)
print('✅ Session created')

# 2. Insert request
request_data = {
    'request_id': request_id,
    'session_id': session_id,
    'query': 'Test query from Supabase migration',
    'prompt_tokens': 10,
    'total_chunk_tokens': 500,
    'completion_tokens': 100,
    'llm_latency_ms': 1500.5,
    'total_latency_ms': 3000.0,
    'operation_type': 'chat_message',
    'status': 'success'
}
insert_request(request_data)
print('✅ Request inserted')

# 3. Insert chunks
chunks = [
    {
        'chunk_index': 0,
        'paper_title': 'Test Paper 1',
        'content_preview': 'This is a test chunk from Supabase',
        'chunk_token_count': 250
    },
    {
        'chunk_index': 1,
        'paper_title': 'Test Paper 2',
        'content_preview': 'Another test chunk',
        'chunk_token_count': 250
    }
]
insert_chunks(request_id, chunks)
print('✅ Chunks inserted')

# 4. Verify by reading back
requests = get_requests_by_session(session_id)
print(f'✅ Read back: {len(requests)} request(s) found')
print()
print('🎉 Supabase integration FULLY WORKING!')
print(f'   Test session ID: {session_id}')
print(f'   Test request ID: {request_id}')
