from fastapi import APIRouter
from db.supabase_client import supabase
from engine.rule_engine import check_rules, fuzzy_match

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.post("/test")
async def test_rule_engine(data: dict):
    """
    Test if a comment matches any rule.
    Use this to verify rule engine works.
    """
    comment = data.get("comment", "")
    influencer_id = data.get("influencer_id", "")
    
    result = await check_rules(comment, influencer_id)
    
    if result:
        return {
            "matched": True,
            "rule": result,
            "action": result.get("action"),
            "template": result.get("template")
        }
    return {
        "matched": False,
        "message": "No rule found - will go to AI"
    }

@router.post("/create")
async def create_rule(data: dict):
    """Create a new automation rule"""
    
    result = supabase.table("rules").insert({
        "influencer_id": data["influencer_id"],
        "post_id": data.get("post_id", None),
        "keywords": data["keywords"],
        "action": data["action"],
        "template": data.get("template", ""),
        "link": data.get("link", ""),
        "priority": data.get("priority", 0)
    }).execute()
    
    return {"status": "created ✅", "rule": result.data[0]}

@router.get("/{influencer_id}")
async def get_rules(influencer_id: str):
    """Get all rules for an influencer"""
    
    result = supabase.table("rules")\
        .select("*")\
        .eq("influencer_id", influencer_id)\
        .order("priority", desc=True)\
        .execute()
    
    return {"rules": result.data}

@router.post("/post-settings")
async def update_post_settings(data: dict):
    """Update reply mode for a specific post"""
    
    influencer_id = data["influencer_id"]
    post_id = data["post_id"]
    mode = data["mode"]  # auto / review / manual
    
    if mode not in ["auto", "review", "manual"]:
        return {"error": "Invalid mode. Use: auto, review, or manual"}
    
    # Check if setting exists
    existing = supabase.table("post_settings")\
        .select("id")\
        .eq("influencer_id", influencer_id)\
        .eq("post_id", post_id)\
        .execute()
    
    if existing.data:
        # Update existing
        supabase.table("post_settings")\
            .update({"mode": mode})\
            .eq("influencer_id", influencer_id)\
            .eq("post_id", post_id)\
            .execute()
    else:
        # Create new
        supabase.table("post_settings").insert({
            "influencer_id": influencer_id,
            "post_id": post_id,
            "mode": mode
        }).execute()
    
    return {
        "status": "updated ✅",
        "post_id": post_id,
        "mode": mode
    }


@router.get("/post-settings/{influencer_id}")
async def get_post_settings(influencer_id: str):
    """Get all post settings for an influencer"""
    
    settings = supabase.table("post_settings")\
        .select("*")\
        .eq("influencer_id", influencer_id)\
        .execute()
    
    return {"settings": settings.data}