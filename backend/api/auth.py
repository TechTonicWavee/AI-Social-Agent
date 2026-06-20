import os
import httpx
from fastapi import APIRouter
from db.supabase_client import supabase
from rag.embeddings import embed_all_existing_replies
from rag.style_analyser import analyze_influencer_style
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

META_API_VERSION = "v19.0"
META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"


# ── Onboarding ────────────────────────────────────────────────────────────────
@router.post("/onboard")
async def onboard_influencer(data: dict):
    """
    Complete onboarding flow for new influencer.
    Creates account, fetches past comments, builds personality.
    """
    
    name = data["name"]
    email = data["email"]
    instagram_id = data.get("instagram_id", f"test_{name.lower()}")
    access_token = data.get("access_token", "")
    
    # Check if already exists
    existing = supabase.table("influencers")\
        .select("id")\
        .eq("email", email)\
        .execute()
    
    if existing.data:
        influencer_id = existing.data[0]["id"]
        print(f"✅ Existing influencer found: {influencer_id}")
    else:
        # Create new influencer
        result = supabase.table("influencers").insert({
            "name": name,
            "email": email,
            "instagram_id": instagram_id,
            "access_token": access_token,
            "default_mode": data.get("default_mode", "auto")
        }).execute()
        
        influencer_id = result.data[0]["id"]
        print(f"✅ New influencer created: {influencer_id}")
    
    # Fetch past comments if access token provided
    comments_imported = 0
    if access_token:
        comments_imported = await fetch_past_comments(
            influencer_id=influencer_id,
            instagram_id=instagram_id,
            access_token=access_token
        )
    
    # Build personality from existing replies
    personality = await analyze_influencer_style(influencer_id)
    
    # Embed all replies
    embedded = await embed_all_existing_replies(influencer_id)
    
    return {
        "status": "onboarded ✅",
        "influencer_id": influencer_id,
        "comments_imported": comments_imported,
        "replies_embedded": embedded,
        "personality": personality
    }


# ── Fetch Past Comments from Instagram ───────────────────────────────────────
async def fetch_past_comments(
    influencer_id: str,
    instagram_id: str,
    access_token: str
) -> int:
    """
    Fetch past comments and replies from Instagram API.
    Stores them as training data.
    """
    
    count = 0
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            
            # Get recent posts
            posts_response = await client.get(
                f"{META_BASE_URL}/{instagram_id}/media",
                params={
                    "fields": "id,caption,timestamp",
                    "access_token": access_token,
                    "limit": 20
                }
            )
            
            posts = posts_response.json()
            
            if "error" in posts:
                print(f"❌ Error fetching posts: {posts['error']}")
                return 0
            
            print(f"✅ Found {len(posts.get('data', []))} posts")
            
            # For each post fetch comments
            for post in posts.get("data", []):
                post_id = post["id"]
                
                comments_response = await client.get(
                    f"{META_BASE_URL}/{post_id}/comments",
                    params={
                        "fields": "id,text,username,timestamp,replies{id,text,username}",
                        "access_token": access_token,
                        "limit": 50
                    }
                )
                
                comments_data = comments_response.json()
                
                for comment in comments_data.get("data", []):
                    
                    # Check if comment already exists
                    existing = supabase.table("comments")\
                        .select("id")\
                        .eq("instagram_comment_id", comment["id"])\
                        .execute()
                    
                    if existing.data:
                        continue
                    
                    # Save comment
                    saved_comment = supabase.table("comments").insert({
                        "influencer_id": influencer_id,
                        "instagram_comment_id": comment["id"],
                        "post_id": post_id,
                        "username": comment.get("username", "unknown"),
                        "text": comment.get("text", ""),
                        "handled_by": "historical",
                        "sentiment": "unknown"
                    }).execute()
                    
                    comment_db_id = saved_comment.data[0]["id"]
                    
                    # Save influencer's replies as training data
                    for reply in comment.get("replies", {}).get("data", []):
                        if reply.get("username") == instagram_id:
                            supabase.table("replies").insert({
                                "comment_id": comment_db_id,
                                "influencer_id": influencer_id,
                                "text": reply["text"],
                                "source": "manual",
                                "status": "sent"
                            }).execute()
                            count += 1
            
            print(f"✅ Imported {count} historical replies")
            return count
            
    except Exception as e:
        print(f"❌ Error fetching past comments: {str(e)}")
        return 0


# ── Add Manual Training Examples ──────────────────────────────────────────────
@router.post("/add-example")
async def add_training_example(data: dict):
    """
    Manually add comment/reply pairs as training data.
    Influencer can add examples from dashboard.
    """
    
    influencer_id = data["influencer_id"]
    examples = data["examples"]  # list of {comment, reply} pairs
    
    saved_count = 0
    
    for example in examples:
        comment_text = example.get("comment", "")
        reply_text = example.get("reply", "")
        
        if not comment_text or not reply_text:
            continue
        
        # Save as training comment
        saved_comment = supabase.table("comments").insert({
            "influencer_id": influencer_id,
            "instagram_comment_id": f"manual_{influencer_id[:8]}_{saved_count}",
            "post_id": "manual_training",
            "username": "training_example",
            "text": comment_text,
            "handled_by": "manual_training",
            "sentiment": "unknown"
        }).execute()
        
        comment_id = saved_comment.data[0]["id"]
        
        # Save reply
        saved_reply = supabase.table("replies").insert({
            "comment_id": comment_id,
            "influencer_id": influencer_id,
            "text": reply_text,
            "source": "manual",
            "status": "sent"
        }).execute()
        
        # Generate and save embedding
        from rag.embeddings import save_reply_with_embedding
        await save_reply_with_embedding(
            reply_id=saved_reply.data[0]["id"],
            comment_text=comment_text,
            reply_text=reply_text
        )
        
        saved_count += 1
    
    return {
        "status": "examples saved ✅",
        "saved_count": saved_count,
        "message": f"Added {saved_count} training examples to AI memory"
    }


# ── Get Influencer Profile ────────────────────────────────────────────────────
@router.get("/profile/{influencer_id}")
async def get_profile(influencer_id: str):
    """Get influencer profile with personality"""
    
    result = supabase.table("influencers")\
        .select("id, name, email, instagram_id, default_mode, personality, created_at")\
        .eq("id", influencer_id)\
        .execute()
    
    if not result.data:
        return {"error": "Influencer not found"}
    
    influencer = result.data[0]
    
    # Get stats
    comments_count = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .execute()
    
    replies_count = supabase.table("replies")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .execute()
    
    return {
        "profile": influencer,
        "stats": {
            "total_comments": comments_count.count or 0,
            "total_replies": replies_count.count or 0
        }
    }