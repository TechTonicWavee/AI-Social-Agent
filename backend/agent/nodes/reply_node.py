from agent.state import CommentState
from db.supabase_client import supabase

async def reply_node(state: CommentState) -> CommentState:
    """Save reply to database based on post mode"""
    
    mode = state.get("post_mode", "auto")
    reply_text = state.get("generated_reply", "")
    
    if not reply_text:
        return {**state, "action_taken": state.get("action_taken", "no_reply")}
    
    print(f"💾 Reply node saving reply (mode: {mode})...")
    
    if mode == "auto":
        # Save as sent
        supabase.table("replies").insert({
            "comment_id": state["comment_id"],
            "influencer_id": state["influencer_id"],
            "text": reply_text,
            "source": "ai",
            "status": "sent"
        }).execute()
        
        # Update comment as handled
        supabase.table("comments")\
            .update({"handled_by": "ai"})\
            .eq("id", state["comment_id"])\
            .execute()
        
        print(f"✅ Reply saved as SENT")
        return {**state, "action_taken": "ai_replied"}
    
    elif mode == "review":
        # Save as pending approval
        supabase.table("replies").insert({
            "comment_id": state["comment_id"],
            "influencer_id": state["influencer_id"],
            "text": reply_text,
            "source": "ai",
            "status": "pending_approval"
        }).execute()
        
        supabase.table("comments")\
            .update({"handled_by": "pending_review"})\
            .eq("id", state["comment_id"])\
            .execute()
        
        print(f"⏳ Reply saved as PENDING APPROVAL")
        return {**state, "action_taken": "pending_review"}
    
    elif mode == "manual":
        supabase.table("comments")\
            .update({"handled_by": "manual"})\
            .eq("id", state["comment_id"])\
            .execute()
        
        print(f"✋ Comment flagged for manual reply")
        return {**state, "action_taken": "flagged_manual"}
    
    return {**state, "action_taken": "unknown"}