from typing import TypedDict, Optional

class CommentState(TypedDict):
    # Input
    comment_id: str
    comment_text: str
    influencer_id: str
    post_id: str
    username: str
    
    # Processing
    sentiment: str
    matched_rule: Optional[dict]
    similar_replies: list
    
    # Output
    generated_reply: str
    action_taken: str
    post_mode: str