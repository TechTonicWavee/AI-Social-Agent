from db.supabase_client import supabase
from rag.embeddings import generate_embedding

async def search_similar_replies(
    comment_text: str,
    influencer_id: str,
    limit: int = 3
) -> list:
    """
    Find most similar past replies using vector similarity.
    Returns list of similar comment/reply pairs for RAG context.
    """
    
    # Generate embedding for the new comment
    embedding = await generate_embedding(f"Comment: {comment_text}")
    
    if not embedding:
        print("⚠️ Could not generate embedding - falling back to keyword search")
        return await keyword_fallback_search(comment_text, influencer_id, limit)
    
    # Pad to 768 dimensions
    if len(embedding) < 768:
        embedding = embedding + [0.0] * (768 - len(embedding))
    elif len(embedding) > 768:
        embedding = embedding[:768]
    
    try:
        # Use pgvector similarity search
        result = supabase.rpc(
            "search_similar_replies",
            {
                "query_embedding": embedding,
                "influencer_uuid": influencer_id,
                "match_count": limit
            }
        ).execute()
        
        if result.data:
            print(f"✅ Vector search found {len(result.data)} similar replies")
            return [
                {
                    "comment": r["comment_text"],
                    "reply": r["reply_text"],
                    "similarity": r["similarity"],
                    "source": r["source"]
                }
                for r in result.data
                if r["similarity"] > 0.5  # only use if 50%+ similar
            ]
        
        print("⚠️ No similar replies found via vector search")
        return []
        
    except Exception as e:
        print(f"❌ Vector search error: {str(e)}")
        return await keyword_fallback_search(comment_text, influencer_id, limit)


async def keyword_fallback_search(
    comment_text: str,
    influencer_id: str,
    limit: int = 3
) -> list:
    """Fallback to keyword search if vector search fails"""
    
    replies = supabase.table("replies")\
        .select("text, comments(text), source")\
        .eq("influencer_id", influencer_id)\
        .eq("status", "sent")\
        .order("created_at", desc=True)\
        .limit(50)\
        .execute()
    
    if not replies.data:
        return []
    
    comment_words = set(comment_text.lower().split())
    scored = []
    
    for reply in replies.data:
        if reply.get("comments"):
            past_comment = reply["comments"]["text"].lower()
            past_words = set(past_comment.split())
            overlap = len(comment_words & past_words)
            if overlap > 0:
                scored.append({
                    "comment": reply["comments"]["text"],
                    "reply": reply["text"],
                    "similarity": overlap / max(len(comment_words), 1),
                    "source": reply.get("source", "ai")
                })
    
    scored.sort(key=lambda x: (x["similarity"], 1 if x["source"] == "manual" else 0), reverse=True)
    return scored[:limit]