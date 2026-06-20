from agent.state import CommentState
from db.supabase_client import supabase
from engine.reply_poster import execute_reply_action
from engine.rule_engine import execute_rule
from rag.embeddings import save_reply_with_embedding

async def reply_node(state: CommentState) -> CommentState:
    """Save reply and post to Instagram"""
    
    mode = state.get("post_mode", "auto")
    reply_text = state.get("generated_reply", "")
    action = state.get("action_taken", "")
    
    # Handle rule match - get reply text from rule
    if state.get("matched_rule") and not reply_text:
        rule_result = await execute_rule(
            state["matched_rule"],
            state["comment_id"]
        )
        reply_text = rule_result.get("text", "")
        action = "rule_reply"
    
    if not reply_text and action not in ["auto_hidden", "flagged_collab"]:
        return {**state, "action_taken": "no_reply"}
    
    print(f"💾 Reply node - mode: {mode}, action: {action}")
    
    if mode == "auto":
        saved_reply = None
        if reply_text:
            saved_reply = supabase.table("replies").insert({
                "comment_id": state["comment_id"],
                "influencer_id": state["influencer_id"],
                "text": reply_text,
                "source": "ai" if not state.get("matched_rule") else "rule",
                "status": "sent"
            }).execute()
            
            # Save embedding for future RAG
            if saved_reply and saved_reply.data:
                await save_reply_with_embedding(
                    reply_id=saved_reply.data[0]["id"],
                    comment_text=state["comment_text"],
                    reply_text=reply_text
                )
        
        supabase.table("comments")\
            .update({"handled_by": action or "ai"})\
            .eq("id", state["comment_id"])\
            .execute()
        
        await execute_reply_action(
            action=action or "ai_replied",
            instagram_comment_id=state["comment_id"],
            reply_text=reply_text,
            influencer_id=state["influencer_id"]
        )
        
        return {**state, "generated_reply": reply_text, "action_taken": action or "ai_replied"}
    
    elif mode == "review":
        if reply_text:
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
        
        print(f"⏳ Reply saved as pending approval")
        return {**state, "generated_reply": reply_text, "action_taken": "pending_review"}
    
    elif mode == "manual":
        supabase.table("comments")\
            .update({"handled_by": "manual"})\
            .eq("id", state["comment_id"])\
            .execute()
        
        print(f"✋ Flagged for manual reply")
        return {**state, "action_taken": "flagged_manual"}
    
    return {**state, "action_taken": "unknown"}