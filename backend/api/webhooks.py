import os
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Query
from db.supabase_client import supabase
from dotenv import load_dotenv
from agent.graph import graph
from engine.reply_poster import execute_reply_action

load_dotenv()

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

# ── Step 1: Meta Webhook Verification ────────────────────────────────────────
@router.get("/instagram")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Meta calls this to verify your webhook URL"""
    
    verify_token = os.getenv("META_VERIFY_TOKEN")
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        print(f"✅ Webhook verified successfully!")
        return int(hub_challenge)
    else:
        print(f"❌ Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


# ── Step 2: Receive Instagram Events ─────────────────────────────────────────
@router.post("/instagram")
async def receive_webhook(request: Request):
    """Meta sends all Instagram events here"""
    
    # Verify the request is genuinely from Meta
    signature = request.headers.get("x-hub-signature-256", "")
    body = await request.body()
    
    if not verify_meta_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    payload = await request.json()
    print(f"📨 Webhook received: {payload}")
    
    # Process each entry Meta sends
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            
            field = change.get("field")
            value = change.get("value", {})
            
            # New comment on a post
            if field == "comments":
                await handle_new_comment(value)
            
            # Someone replied to a comment
            elif field == "comment_replies":
                await handle_manual_reply(value)
    
    # Must return 200 quickly or Meta will retry
    return {"status": "ok"}


# ── Step 3: Handle New Comment ────────────────────────────────────────────────
async def handle_new_comment(value: dict):
    """Save incoming comment to database and process with agent"""
    
    try:
        comment_id = value.get("id")
        comment_text = value.get("text", "")
        post_id = value.get("media", {}).get("id", "")
        username = value.get("from", {}).get("username", "unknown")
        instagram_user_id = value.get("from", {}).get("id", "")
        
        print(f"💬 New comment from @{username}: '{comment_text}'")
        
        influencer = supabase.table("influencers")\
            .select("id")\
            .eq("instagram_id", instagram_user_id)\
            .execute()
        
        if not influencer.data:
            print(f"⚠️ No influencer found for instagram_id: {instagram_user_id}")
            return
        
        influencer_id = influencer.data[0]["id"]
        
        existing = supabase.table("comments")\
            .select("id")\
            .eq("instagram_comment_id", comment_id)\
            .execute()
        
        if existing.data:
            print(f"⚠️ Duplicate comment ignored: {comment_id}")
            return
        
        saved = supabase.table("comments").insert({
            "influencer_id": influencer_id,
            "instagram_comment_id": comment_id,
            "post_id": post_id,
            "username": username,
            "text": comment_text,
            "handled_by": "pending",
            "sentiment": "unknown"
        }).execute()
        
        db_comment_id = saved.data[0]["id"]
        print(f"✅ Comment saved: {comment_id}")
        
        # 🚀 Run through full LangGraph agent
        result = await graph.ainvoke({
            "comment_id": db_comment_id,
            "comment_text": comment_text,
            "influencer_id": influencer_id,
            "post_id": post_id,
            "username": username,
            "sentiment": "",
            "matched_rule": None,
            "similar_replies": [],
            "generated_reply": "",
            "action_taken": "",
            "post_mode": ""
        })
        
        print(f"✅ Agent completed: {result['action_taken']}")
        
    except Exception as e:
        print(f"❌ Error handling comment: {str(e)}")


# ── Step 4: Handle Manual Reply from Influencer ───────────────────────────────
async def handle_manual_reply(value: dict):
    """When influencer replies manually on Instagram - save as training data"""
    
    try:
        comment_id = value.get("parent_id")
        reply_text = value.get("text", "")
        
        print(f"📝 Manual reply detected: '{reply_text}'")
        
        # Find the original comment
        original = supabase.table("comments")\
            .select("*")\
            .eq("instagram_comment_id", comment_id)\
            .execute()
        
        if not original.data:
            print(f"⚠️ Original comment not found: {comment_id}")
            return
        
        comment = original.data[0]
        
        # Save as training data
        supabase.table("replies").insert({
            "comment_id": comment["id"],
            "influencer_id": comment["influencer_id"],
            "text": reply_text,
            "source": "manual",  # manual replies = highest quality training data
            "status": "sent"
        }).execute()
        
        print(f"✅ Manual reply saved as training data")
        
    except Exception as e:
        print(f"❌ Error handling manual reply: {str(e)}")


# ── Helper: Verify Meta Signature ─────────────────────────────────────────────
def verify_meta_signature(body: bytes, signature: str) -> bool:
    """Verify request is genuinely from Meta"""
    
    app_secret = os.getenv("META_APP_SECRET", "")
    
    if not app_secret:
        print("⚠️ META_APP_SECRET not set - skipping signature verification")
        return True  # Skip during development
    
    expected = "sha256=" + hmac.new(
        app_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)