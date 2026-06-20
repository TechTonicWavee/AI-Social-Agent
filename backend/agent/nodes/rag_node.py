from agent.state import CommentState
from rag.vector_search import search_similar_replies

async def rag_node(state: CommentState) -> CommentState:
    """Search for similar past replies using vector search"""
    
    print(f"🔍 RAG node - vector searching for similar replies...")
    
    similar = await search_similar_replies(
        comment_text=state["comment_text"],
        influencer_id=state["influencer_id"],
        limit=3
    )
    
    if similar:
        print(f"✅ Found {len(similar)} similar replies")
        for s in similar:
            print(f"   Similarity: {s['similarity']:.2f} | Reply: '{s['reply'][:50]}...'")
    else:
        print("⚠️ No similar replies found - AI will use default style")
    
    return {**state, "similar_replies": similar}