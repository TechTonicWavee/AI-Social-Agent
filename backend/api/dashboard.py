from fastapi import APIRouter
from engine.sentiment import detect_sentiment, should_auto_hide, should_flag_for_collab
from agent.graph import graph
from db.supabase_client import supabase
from rag.embeddings import embed_all_existing_replies
from rag.style_analyser import analyze_influencer_style
from rag.vector_search import search_similar_replies

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.post("/test-sentiment")
async def test_sentiment(data: dict):
    comment = data.get("comment", "")
    sentiment = await detect_sentiment(comment)
    auto_hide = should_auto_hide(sentiment, comment)
    flag_collab = should_flag_for_collab(sentiment)
    return {
        "comment": comment,
        "sentiment": sentiment,
        "auto_hide": auto_hide,
        "flag_as_collab": flag_collab,
        "recommended_action": get_recommended_action(sentiment)
    }

def get_recommended_action(sentiment: str) -> str:
    actions = {
        "question": "Send to AI for detailed reply",
        "compliment": "Send warm thank you reply",
        "complaint": "Send calm professional reply",
        "spam": "Auto hide comment",
        "collab": "Flag for influencer review",
        "troll": "Auto hide comment",
        "other": "Send to AI for reply"
    }
    return actions.get(sentiment, "Send to AI")

@router.post("/test-agent")
async def test_agent(data: dict):
    saved = supabase.table("comments").insert({
        "influencer_id": data["influencer_id"],
        "instagram_comment_id": f"test_{data['comment'][:10]}",
        "post_id": data.get("post_id", "test_post"),
        "username": data.get("username", "test_user"),
        "text": data["comment"],
        "handled_by": "pending",
        "sentiment": "unknown"
    }).execute()
    
    comment_id = saved.data[0]["id"]
    
    result = await graph.ainvoke({
        "comment_id": comment_id,
        "comment_text": data["comment"],
        "influencer_id": data["influencer_id"],
        "post_id": data.get("post_id", "test_post"),
        "username": data.get("username", "test_user"),
        "sentiment": "",
        "matched_rule": None,
        "similar_replies": [],
        "generated_reply": "",
        "action_taken": "",
        "post_mode": ""
    })
    
    return {
        "comment": data["comment"],
        "sentiment": result["sentiment"],
        "action_taken": result["action_taken"],
        "generated_reply": result["generated_reply"],
        "post_mode": result["post_mode"],
        "rule_matched": result["matched_rule"] is not None
    }

@router.post("/analyze-style")
async def analyze_style(data: dict):
    influencer_id = data["influencer_id"]
    embedded_count = await embed_all_existing_replies(influencer_id)
    personality = await analyze_influencer_style(influencer_id)
    return {
        "replies_embedded": embedded_count,
        "personality": personality
    }

@router.post("/test-rag")
async def test_rag(data: dict):
    results = await search_similar_replies(
        comment_text=data["comment"],
        influencer_id=data["influencer_id"]
    )
    return {
        "comment": data["comment"],
        "similar_replies_found": len(results),
        "results": results
    }