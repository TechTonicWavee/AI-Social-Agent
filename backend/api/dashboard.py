from fastapi import APIRouter
from engine.sentiment import detect_sentiment, should_auto_hide, should_flag_for_collab

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.post("/test-sentiment")
async def test_sentiment(data: dict):
    """Test sentiment detection on any comment"""
    
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