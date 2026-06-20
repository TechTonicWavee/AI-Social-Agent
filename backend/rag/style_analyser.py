from db.supabase_client import supabase
from models.ollama_client import model
from langchain_core.messages import HumanMessage
import json

async def analyze_influencer_style(influencer_id: str) -> dict:
    """
    Analyze influencer's reply history to extract personality traits.
    Runs once on onboarding, updates periodically.
    """
    
    # Get last 50 replies
    replies = supabase.table("replies")\
        .select("text")\
        .eq("influencer_id", influencer_id)\
        .eq("status", "sent")\
        .order("created_at", desc=True)\
        .limit(50)\
        .execute()
    
    if not replies.data or len(replies.data) < 5:
        print("⚠️ Not enough replies to analyze style")
        return get_default_personality()
    
    reply_texts = [r["text"] for r in replies.data]
    sample = "\n".join([f"- {r}" for r in reply_texts[:20]])
    
    prompt = f"""Analyze these Instagram replies and extract the personality traits.

Replies:
{sample}

Return ONLY a valid JSON object with these exact fields:
{{
    "tone": "friendly/professional/casual/formal",
    "uses_emojis": true/false,
    "common_emojis": ["❤️", "😊"],
    "avg_length": "short/medium/long",
    "language": "english/hindi/hinglish",
    "greeting_style": "hey/hi/none",
    "asks_questions": true/false,
    "personality_summary": "one sentence description"
}}

Return only the JSON, no other text:"""

    try:
        response = model.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        
        # Clean up if model added markdown
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        personality = json.loads(text.strip())
        
        # Save to database
        supabase.table("influencers")\
            .update({"personality": personality})\
            .eq("id", influencer_id)\
            .execute()
        
        print(f"✅ Personality analyzed: {personality['personality_summary']}")
        return personality
        
    except Exception as e:
        print(f"❌ Style analysis error: {str(e)}")
        return get_default_personality()


def get_default_personality() -> dict:
    return {
        "tone": "friendly",
        "uses_emojis": True,
        "common_emojis": ["❤️", "😊", "✨"],
        "avg_length": "short",
        "language": "english",
        "greeting_style": "hey",
        "asks_questions": False,
        "personality_summary": "Friendly and warm influencer"
    }