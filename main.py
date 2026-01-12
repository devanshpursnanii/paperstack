"""
Main Entry Point: Paper Brain AI System

Run the complete paper discovery and RAG pipeline with session logging.
"""

import asyncio
from ai.brain import paper_brain_interface
from ai.rag import multi_paper_rag_with_documents
from ai.logger import SessionLogger


if __name__ == "__main__":
    # Get initial query for session logging
    print("\n" + "="*80)
    print("PAPER BRAIN AI SYSTEM")
    print("="*80 + "\n")
    
    initial_query = input("🔍 What research topic would you like to explore? ").strip()
    
    if not initial_query:
        print("❌ No query provided. Exiting.")
        exit()
    
    # Create session logger
    logger = SessionLogger(query_title=initial_query, mode="paper_brain")
    print(f"\n📝 Session started: {logger.session_id}\n")
    
    # Run Paper Brain agent with logger
    documents = asyncio.run(paper_brain_interface(logger))
    
    if documents:
        # Update mode to RAG
        logger.mode = "multi_paper_rag"
        
        # Switch to Main RAG
        print(f"\n{'='*80}")
        print(f"{'MAIN RAG CHAT - ASK QUESTIONS ABOUT YOUR PAPERS':^80}")
        print(f"{'='*80}\n")
        
        # RAG chat loop
        while True:
            query = input("\n📚 Ask about your papers (or 'quit'): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                # Save session logs
                log_file = logger.save_session()
                print(f"\n💾 Session saved: {log_file}")
                
                # Print summary
                summary = logger.get_summary()
                print(f"\n{'─'*80}")
                print("SESSION SUMMARY")
                print(f"{'─'*80}")
                print(f"📊 RAG chunks logged: {summary['rag_chunks_count']}")
                print(f"🔌 Embedding calls: {summary['embedding_calls_count']}")
                print(f"🤖 LLM calls: {summary['llm_calls_count']}")
                print(f"📝 Total tokens: {summary['total_input_tokens'] + summary['total_output_tokens']}")
                print(f"   ↳ Input: {summary['total_input_tokens']}")
                print(f"   ↳ Output: {summary['total_output_tokens']}")
                
                print("\n👋 Thanks for using Paper Brain!")
                break
            
            if not query:
                continue
            
            try:
                response = multi_paper_rag_with_documents(documents, query, logger)
                print(f"\n{'─'*80}")
                print("ANSWER")
                print(f"{'─'*80}\n")
                print(str(response))
            except Exception as e:
                print(f"❌ Error: {e}")
    else:
        # Save session even if no documents loaded
        log_file = logger.save_session()
        print(f"\n💾 Session saved: {log_file}")
