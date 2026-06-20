from fastapi import APIRouter
from db.supabase_client import supabase
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/{influencer_id}/overview")
async def get_overview(influencer_id: str):
    """Main dashboard overview stats"""
    
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Total comments
    total = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .execute()
    
    # Today's comments
    today_comments = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .gte("created_at", today.isoformat())\
        .execute()
    
    # This week
    week_comments = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .gte("created_at", week_ago.isoformat())\
        .execute()
    
    # Handled by AI
    ai_handled = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .eq("handled_by", "ai")\
        .execute()
    
    # Handled by rules
    rule_handled = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .eq("handled_by", "rule_reply")\
        .execute()
    
    # Pending review
    pending = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .eq("handled_by", "pending_review")\
        .execute()
    
    # Auto hidden (spam)
    hidden = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .eq("handled_by", "auto_hidden")\
        .execute()
    
    # Collab requests
    collabs = supabase.table("comments")\
        .select("id", count="exact")\
        .eq("influencer_id", influencer_id)\
        .eq("handled_by", "flagged_collab")\
        .execute()
    
    total_count = total.count or 0
    ai_count = ai_handled.count or 0
    rule_count = rule_handled.count or 0
    
    return {
        "overview": {
            "total_comments": total_count,
            "today": today_comments.count or 0,
            "this_week": week_comments.count or 0,
            "pending_review": pending.count or 0,
            "collab_requests": collabs.count or 0,
            "auto_hidden": hidden.count or 0
        },
        "breakdown": {
            "ai_handled": ai_count,
            "rule_handled": rule_count,
            "ai_percentage": round((ai_count / total_count * 100) if total_count > 0 else 0, 1),
            "rule_percentage": round((rule_count / total_count * 100) if total_count > 0 else 0, 1)
        }
    }


@router.get("/{influencer_id}/recent-replies")
async def get_recent_replies(influencer_id: str, limit: int = 20):
    """Get recent replies feed for dashboard"""
    
    replies = supabase.table("replies")\
        .select("*, comments(text, username, post_id)")\
        .eq("influencer_id", influencer_id)\
        .eq("status", "sent")\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    
    feed = []
    for reply in replies.data:
        comment = reply.get("comments", {})
        feed.append({
            "reply_id": reply["id"],
            "comment_text": comment.get("text", ""),
            "username": comment.get("username", ""),
            "reply_text": reply["text"],
            "source": reply["source"],
            "created_at": reply["created_at"]
        })
    
    return {"replies": feed, "total": len(feed)}


@router.get("/{influencer_id}/pending-approvals")
async def get_pending_approvals(influencer_id: str):
    """Get all replies waiting for influencer approval"""
    
    pending = supabase.table("replies")\
        .select("*, comments(text, username, post_id)")\
        .eq("influencer_id", influencer_id)\
        .eq("status", "pending_approval")\
        .order("created_at", desc=True)\
        .execute()
    
    approvals = []
    for reply in pending.data:
        comment = reply.get("comments", {})
        approvals.append({
            "reply_id": reply["id"],
            "comment_id": reply["comment_id"],
            "comment_text": comment.get("text", ""),
            "username": comment.get("username", ""),
            "suggested_reply": reply["text"],
            "created_at": reply["created_at"]
        })
    
    return {
        "pending": approvals,
        "total": len(approvals)
    }


@router.post("/{influencer_id}/approve-reply")
async def approve_reply(influencer_id: str, data: dict):
    """Approve or edit a pending reply"""
    
    reply_id = data["reply_id"]
    final_text = data.get("text")  # None = approve as is, text = edited version
    action = data.get("action", "approve")  # approve / reject
    
    if action == "reject":
        supabase.table("replies")\
            .update({"status": "rejected"})\
            .eq("id", reply_id)\
            .execute()
        return {"status": "rejected ✅"}
    
    # Get reply details
    reply = supabase.table("replies")\
        .select("*, comments(instagram_comment_id)")\
        .eq("id", reply_id)\
        .execute()
    
    if not reply.data:
        return {"error": "Reply not found"}
    
    reply_data = reply.data[0]
    approved_text = final_text or reply_data["text"]
    
    # Update reply as sent
    supabase.table("replies")\
        .update({
            "status": "sent",
            "text": approved_text,
            "was_edited": final_text is not None
        })\
        .eq("id", reply_id)\
        .execute()
    
    # Update comment status
    supabase.table("comments")\
        .update({"handled_by": "ai_approved"})\
        .eq("id", reply_data["comment_id"])\
        .execute()
    
    # TODO: Post to Instagram in Prompt 10
    print(f"✅ Reply approved: '{approved_text[:50]}...'")
    
    return {
        "status": "approved ✅",
        "reply_text": approved_text,
        "was_edited": final_text is not None
    }


@router.get("/{influencer_id}/sentiment-breakdown")
async def get_sentiment_breakdown(influencer_id: str):
    """Get breakdown of comment sentiments"""
    
    sentiments = ["question", "compliment", "complaint", "spam", "collab", "troll", "other"]
    breakdown = {}
    
    for sentiment in sentiments:
        result = supabase.table("comments")\
            .select("id", count="exact")\
            .eq("influencer_id", influencer_id)\
            .eq("sentiment", sentiment)\
            .execute()
        breakdown[sentiment] = result.count or 0
    
    return {"sentiment_breakdown": breakdown}


@router.get("/{influencer_id}/collab-requests")
async def get_collab_requests(influencer_id: str):
    """Get all detected collaboration requests"""
    
    collabs = supabase.table("comments")\
        .select("id, username, text, created_at")\
        .eq("influencer_id", influencer_id)\
        .eq("handled_by", "flagged_collab")\
        .order("created_at", desc=True)\
        .execute()
    
    return {
        "collab_requests": collabs.data,
        "total": len(collabs.data)
    }