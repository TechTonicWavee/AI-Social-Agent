from db.supabase_client import supabase
from difflib import SequenceMatcher

def similarity_score(word1: str, word2: str) -> float:
    """Check how similar two words are — handles typos"""
    return SequenceMatcher(None, word1.lower(), word2.lower()).ratio()

def fuzzy_match(comment: str, keywords: list) -> bool:
    """
    Check if comment matches any keyword.
    Handles typos, partial matches, case differences.
    Example: 'produc' matches 'product'
    """
    comment_words = comment.lower().split()
    
    for keyword in keywords:
        keyword = keyword.lower()
        
        # Direct match — fastest check
        if keyword in comment.lower():
            return True
        
        # Fuzzy match — handles typos
        for word in comment_words:
            score = similarity_score(word, keyword)
            if score >= 0.80:  # 80% similar = match
                return True
    
    return False

async def check_rules(
    comment_text: str,
    influencer_id: str,
    post_id: str = None
) -> dict | None:
    """
    Check if comment matches any rule.
    Returns the matching rule or None if no match.
    
    Priority order:
    1. Post-specific rules (highest priority)
    2. Global rules (apply to all posts)
    """
    
    # Fetch post-specific rules first
    if post_id:
        post_rules = supabase.table("rules")\
            .select("*")\
            .eq("influencer_id", influencer_id)\
            .eq("post_id", post_id)\
            .order("priority", desc=True)\
            .execute()
        
        for rule in post_rules.data:
            if fuzzy_match(comment_text, rule["keywords"]):
                print(f"✅ Rule matched (post-specific): {rule['keywords']}")
                return rule
    
    # Then check global rules
    global_rules = supabase.table("rules")\
        .select("*")\
        .eq("influencer_id", influencer_id)\
        .is_("post_id", "null")\
        .order("priority", desc=True)\
        .execute()
    
    for rule in global_rules.data:
        if fuzzy_match(comment_text, rule["keywords"]):
            print(f"✅ Rule matched (global): {rule['keywords']}")
            return rule
    
    print(f"❌ No rule matched for: '{comment_text}'")
    return None

async def execute_rule(rule: dict, comment_id: str) -> dict:
    """
    Execute the matched rule action.
    Returns what action was taken.
    """
    action = rule.get("action")
    template = rule.get("template", "")
    link = rule.get("link", "")
    
    if action == "reply":
        return {
            "action": "reply",
            "text": template,
            "comment_id": comment_id
        }
    
    elif action == "dm":
        return {
            "action": "dm",
            "text": template,
            "link": link,
            "comment_id": comment_id
        }
    
    elif action == "hide":
        return {
            "action": "hide",
            "comment_id": comment_id
        }
    
    elif action == "flag":
        return {
            "action": "flag",
            "comment_id": comment_id,
            "reason": template
        }
    
    return {"action": "none"}