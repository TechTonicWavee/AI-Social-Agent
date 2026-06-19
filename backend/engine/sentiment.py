from models.ollama_client import model
from langchain_core.messages import HumanMessage

async def detect_sentiment(comment_text: str) -> str:
    """
    Classify comment into one of these categories:
    - question: asking something
    - compliment: saying something nice
    - complaint: unhappy about something
    - spam: promotional/irrelevant
    - collab: brand/collaboration request
    - troll: mean/offensive comment
    - other: anything else
    """
    
    prompt = f"""Classify this Instagram comment into exactly ONE category.

Categories:
- question: asking a question
- compliment: positive/nice comment
- complaint: negative/unhappy comment  
- spam: promotional or irrelevant
- collab: brand deal or collaboration request
- troll: offensive or mean comment
- other: anything else

Comment: "{comment_text}"

Reply with ONLY the category word. Nothing else. No explanation."""

    try:
        response = model.invoke([HumanMessage(content=prompt)])
        sentiment = response.content.strip().lower()
        
        # Validate it's one of our categories
        valid = ["question", "compliment", "complaint", "spam", "collab", "troll", "other"]
        
        if sentiment not in valid:
            # Try to extract valid word if model added extra text
            for word in valid:
                if word in sentiment:
                    return word
            return "other"
        
        print(f"🎯 Sentiment detected: '{comment_text}' → {sentiment}")
        return sentiment
        
    except Exception as e:
        print(f"❌ Sentiment detection error: {str(e)}")
        return "other"


def should_auto_hide(sentiment: str, comment_text: str) -> bool:
    """Decide if comment should be hidden automatically"""
    
    # Always hide spam and trolls
    if sentiment in ["spam", "troll"]:
        return True
    
    # Hide comments with offensive words
    offensive_words = ["scam", "fake", "fraud", "cheat", "liar"]
    comment_lower = comment_text.lower()
    
    for word in offensive_words:
        if word in comment_lower:
            return True
    
    return False


def should_flag_for_collab(sentiment: str) -> bool:
    """Flag collaboration requests for influencer to review"""
    return sentiment == "collab"