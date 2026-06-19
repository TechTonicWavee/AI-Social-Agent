from agent.state import CommentState
from engine.sentiment import detect_sentiment, should_auto_hide, should_flag_for_collab
from db.supabase_client import supabase

async def sentiment_node(state: CommentState) -> CommentState:
    """Detect sentiment and handle spam/collab immediately"""
    
    print(f"🎯 Sentiment node processing: '{state['comment_text']}'")
    
    sentiment = await detect_sentiment(state["comment_text"])
    
    # Update sentiment in database
    supabase.table("comments")\
        .update({"sentiment": sentiment})\
        .eq("id", state["comment_id"])\
        .execute()
    
    # Auto hide spam and trolls
    if should_auto_hide(sentiment, state["comment_text"]):
        supabase.table("comments")\
            .update({"handled_by": "auto_hidden"})\
            .eq("id", state["comment_id"])\
            .execute()
        return {
            **state,
            "sentiment": sentiment,
            "action_taken": "auto_hidden",
            "generated_reply": ""
        }
    
    # Flag collaboration requests
    if should_flag_for_collab(sentiment):
        supabase.table("comments")\
            .update({"handled_by": "flagged_collab"})\
            .eq("id", state["comment_id"])\
            .execute()
        return {
            **state,
            "sentiment": sentiment,
            "action_taken": "flagged_collab",
            "generated_reply": ""
        }
    
    return {**state, "sentiment": sentiment}