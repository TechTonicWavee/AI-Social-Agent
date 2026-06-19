from langgraph.graph import StateGraph, END
from agent.state import CommentState
from agent.nodes.sentiment_node import sentiment_node
from agent.nodes.rag_node import rag_node
from agent.nodes.llm_node import llm_node
from agent.nodes.reply_node import reply_node
from engine.rule_engine import check_rules, execute_rule
from db.supabase_client import supabase

async def rule_check_node(state: CommentState) -> CommentState:
    """Check if comment matches any automation rule"""
    
    print(f"⚡ Checking rules for: '{state['comment_text']}'")
    
    matched_rule = await check_rules(
        state["comment_text"],
        state["influencer_id"],
        state.get("post_id")
    )
    
    return {**state, "matched_rule": matched_rule}

async def get_post_mode(state: CommentState) -> CommentState:
    """Get the reply mode for this specific post"""
    
    post_id = state.get("post_id")
    influencer_id = state["influencer_id"]
    
    # Check post-specific setting
    if post_id:
        setting = supabase.table("post_settings")\
            .select("mode")\
            .eq("influencer_id", influencer_id)\
            .eq("post_id", post_id)\
            .execute()
        
        if setting.data:
            return {**state, "post_mode": setting.data[0]["mode"]}
    
    # Fall back to influencer default
    influencer = supabase.table("influencers")\
        .select("default_mode")\
        .eq("id", influencer_id)\
        .execute()
    
    mode = influencer.data[0]["default_mode"] if influencer.data else "auto"
    return {**state, "post_mode": mode}

# ── Routing Functions ─────────────────────────────────────────────────────────

def route_by_mode(state: CommentState) -> str:
    """Route based on post mode"""
    mode = state.get("post_mode", "auto")
    if mode == "manual":
        return "reply_node"  # just flag it
    return "rule_check_node"  # continue processing

def route_after_rule(state: CommentState) -> str:
    """Route based on rule match result"""
    if state.get("matched_rule"):
        return "reply_node"  # rule matched, go straight to save
    return "sentiment_node"  # no rule, check sentiment

def route_after_sentiment(state: CommentState) -> str:
    """Route based on sentiment result"""
    action = state.get("action_taken", "")
    if action in ["auto_hidden", "flagged_collab"]:
        return END  # already handled
    return "rag_node"  # continue to generate reply

# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph():
    workflow = StateGraph(CommentState)
    
    # Add all nodes
    workflow.add_node("get_post_mode", get_post_mode)
    workflow.add_node("rule_check_node", rule_check_node)
    workflow.add_node("sentiment_node", sentiment_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("llm_node", llm_node)
    workflow.add_node("reply_node", reply_node)
    
    # Entry point
    workflow.set_entry_point("get_post_mode")
    
    # Edges
    workflow.add_conditional_edges(
        "get_post_mode",
        route_by_mode,
        {
            "reply_node": "reply_node",
            "rule_check_node": "rule_check_node"
        }
    )
    
    workflow.add_conditional_edges(
        "rule_check_node",
        route_after_rule,
        {
            "reply_node": "reply_node",
            "sentiment_node": "sentiment_node"
        }
    )
    
    workflow.add_conditional_edges(
        "sentiment_node",
        route_after_sentiment,
        {
            END: END,
            "rag_node": "rag_node"
        }
    )
    
    workflow.add_edge("rag_node", "llm_node")
    workflow.add_edge("llm_node", "reply_node")
    workflow.add_edge("reply_node", END)
    
    return workflow.compile()

# Single instance
graph = build_graph()