from agent.state import CommentState
from db.supabase_client import supabase
from models.ollama_client import model
from langchain_core.messages import HumanMessage

async def generate_embedding(text: str) -> list:
    """Generate simple embedding using Ollama"""
    try:
        # Use Ollama embeddings
        import httpx
        response = httpx.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "llama3.2", "prompt": text}
        )
        return response.json().get("embedding", [])
    except Exception as e:
        print(f"❌ Embedding error: {str(e)}")
        return []

async def rag_node(state: CommentState) -> CommentState:
    """Search for similar past replies to use as style context"""
    
    print(f"🔍 RAG node searching for similar replies...")
    
    try:
        # Get past replies for this influencer
        past_replies = supabase.table("replies")\
            .select("*, comments(text)")\
            .eq("influencer_id", state["influencer_id"])\
            .eq("status", "sent")\
            .order("created_at", desc=True)\
            .limit(100)\
            .execute()
        
        if not past_replies.data:
            print("⚠️ No past replies found - using default style")
            return {**state, "similar_replies": []}
        
        # Simple keyword similarity search
        # (Full vector search added in Prompt 7)
        comment_words = set(state["comment_text"].lower().split())
        scored_replies = []
        
        for reply in past_replies.data:
            if reply.get("comments"):
                past_comment = reply["comments"]["text"].lower()
                past_words = set(past_comment.split())
                
                # Calculate word overlap score
                overlap = len(comment_words & past_words)
                if overlap > 0:
                    scored_replies.append({
                        "score": overlap,
                        "comment": reply["comments"]["text"],
                        "reply": reply["text"],
                        "source": reply["source"]
                    })
        
        # Sort by score, prioritize manual replies
        scored_replies.sort(
            key=lambda x: (x["score"], 1 if x["source"] == "manual" else 0),
            reverse=True
        )
        
        top_replies = scored_replies[:3]
        print(f"✅ Found {len(top_replies)} similar past replies")
        
        return {**state, "similar_replies": top_replies}
        
    except Exception as e:
        print(f"❌ RAG error: {str(e)}")
        return {**state, "similar_replies": []}