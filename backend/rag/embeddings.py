import httpx
from db.supabase_client import supabase

OLLAMA_URL = "http://localhost:11434"

async def generate_embedding(text: str) -> list | None:
    """Generate embedding vector using Ollama"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={
                    "model": "llama3.2",
                    "prompt": text
                }
            )
            result = response.json()
            embedding = result.get("embedding", [])
            
            if embedding:
                print(f"✅ Embedding generated: {len(embedding)} dimensions")
                return embedding
            else:
                print(f"❌ Empty embedding returned")
                return None
                
    except Exception as e:
        print(f"❌ Embedding error: {str(e)}")
        return None


async def save_reply_with_embedding(
    reply_id: str,
    comment_text: str,
    reply_text: str
) -> bool:
    """Generate and save embedding for a reply"""
    
    # Combine comment + reply for better embedding
    combined_text = f"Comment: {comment_text}\nReply: {reply_text}"
    
    embedding = await generate_embedding(combined_text)
    
    if not embedding:
        return False
    
    # Pad or truncate to 768 dimensions if needed
    if len(embedding) < 768:
        embedding = embedding + [0.0] * (768 - len(embedding))
    elif len(embedding) > 768:
        embedding = embedding[:768]
    
    try:
        supabase.table("replies")\
            .update({"embedding": embedding})\
            .eq("id", reply_id)\
            .execute()
        
        print(f"✅ Embedding saved for reply: {reply_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving embedding: {str(e)}")
        return False


async def embed_all_existing_replies(influencer_id: str) -> int:
    """
    Generate embeddings for all past replies that don't have one yet.
    Called during influencer onboarding.
    """
    
    # Get replies without embeddings
    replies = supabase.table("replies")\
        .select("id, text, comment_id, comments(text)")\
        .eq("influencer_id", influencer_id)\
        .is_("embedding", "null")\
        .execute()
    
    if not replies.data:
        print("✅ All replies already have embeddings")
        return 0
    
    count = 0
    for reply in replies.data:
        comment_text = ""
        if reply.get("comments"):
            comment_text = reply["comments"]["text"]
        
        success = await save_reply_with_embedding(
            reply_id=reply["id"],
            comment_text=comment_text,
            reply_text=reply["text"]
        )
        
        if success:
            count += 1
    
    print(f"✅ Embedded {count}/{len(replies.data)} replies")
    return count