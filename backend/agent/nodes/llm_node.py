from agent.state import CommentState
from models.ollama_client import model
from langchain_core.messages import HumanMessage

async def llm_node(state: CommentState) -> CommentState:
    """Generate reply using Ollama with influencer style context"""
    
    print(f"🤖 LLM node generating reply...")
    
    # Build context from similar past replies
    style_context = ""
    if state["similar_replies"]:
        style_context = "Here are examples of how this influencer replies:\n\n"
        for example in state["similar_replies"]:
            style_context += f"Comment: {example['comment']}\n"
            style_context += f"Reply: {example['reply']}\n"
            style_context += "---\n"
    
    sentiment = state.get("sentiment", "other")
    
    # Tone instructions based on sentiment
    tone_map = {
        "question": "Answer helpfully and warmly.",
        "compliment": "Reply with genuine gratitude, be warm and personal.",
        "complaint": "Reply calmly and professionally, show empathy.",
        "other": "Reply in a friendly and engaging way."
    }
    tone = tone_map.get(sentiment, tone_map["other"])
    
    prompt = f"""You are replying to an Instagram comment on behalf of an influencer.

{style_context}

Instructions:
- Reply in English only
- Keep reply short (1-2 sentences max)
- Sound natural and human, not robotic
- {tone}
- Match the style from the examples above if provided
- Do not start with "I" 
- Do not mention you are an AI

Comment from @{state['username']}: "{state['comment_text']}"

Write only the reply, nothing else:"""

    try:
        response = model.invoke([HumanMessage(content=prompt)])
        reply = response.content.strip()
        
        # Clean up common AI artifacts
        reply = reply.replace('"', '').replace("Reply:", "").strip()
        
        print(f"✅ Generated reply: '{reply}'")
        return {**state, "generated_reply": reply}
        
    except Exception as e:
        print(f"❌ LLM error: {str(e)}")
        return {
            **state,
            "generated_reply": "Thanks for your comment! 😊"
        }