import os
import httpx
from dotenv import load_dotenv
from db.supabase_client import supabase

load_dotenv()

META_API_VERSION = "v19.0"
META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"

async def get_access_token(influencer_id: str) -> str | None:
    """Get influencer's Instagram access token from database"""
    result = supabase.table("influencers")\
        .select("access_token")\
        .eq("id", influencer_id)\
        .execute()
    
    if result.data:
        return result.data[0]["access_token"]
    return None

async def post_comment_reply(
    comment_id: str,
    reply_text: str,
    influencer_id: str
) -> bool:
    """Post a reply to an Instagram comment"""
    
    access_token = await get_access_token(influencer_id)
    if not access_token:
        print(f"❌ No access token for influencer: {influencer_id}")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{META_BASE_URL}/{comment_id}/replies",
                data={
                    "message": reply_text,
                    "access_token": access_token
                }
            )
            
            result = response.json()
            
            if "id" in result:
                print(f"✅ Reply posted to Instagram: {result['id']}")
                return True
            else:
                print(f"❌ Failed to post reply: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Error posting reply: {str(e)}")
        return False


async def send_dm(
    instagram_user_id: str,
    message: str,
    link: str,
    influencer_id: str
) -> bool:
    """Send a direct message to a user"""
    
    access_token = await get_access_token(influencer_id)
    if not access_token:
        return False
    
    # Combine message and link
    full_message = f"{message}\n\n{link}" if link else message
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{META_BASE_URL}/me/messages",
                data={
                    "recipient": f'{{"id":"{instagram_user_id}"}}',
                    "message": f'{{"text":"{full_message}"}}',
                    "access_token": access_token
                }
            )
            
            result = response.json()
            
            if "message_id" in result:
                print(f"✅ DM sent successfully")
                return True
            else:
                print(f"❌ Failed to send DM: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending DM: {str(e)}")
        return False


async def hide_comment(
    comment_id: str,
    influencer_id: str
) -> bool:
    """Hide a spam or troll comment"""
    
    access_token = await get_access_token(influencer_id)
    if not access_token:
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{META_BASE_URL}/{comment_id}",
                data={
                    "hide": "true",
                    "access_token": access_token
                }
            )
            
            result = response.json()
            
            if result.get("success"):
                print(f"✅ Comment hidden successfully")
                return True
            else:
                print(f"❌ Failed to hide comment: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Error hiding comment: {str(e)}")
        return False


async def execute_reply_action(
    action: str,
    instagram_comment_id: str,
    reply_text: str,
    influencer_id: str,
    instagram_user_id: str = None,
    link: str = None
) -> bool:
    """
    Main function - execute the right action based on what agent decided
    Called from webhook after agent processes comment
    """
    
    print(f"📤 Executing action: {action}")
    
    if action == "ai_replied" or action == "rule_reply":
        return await post_comment_reply(
            instagram_comment_id,
            reply_text,
            influencer_id
        )
    
    elif action == "dm":
        return await send_dm(
            instagram_user_id,
            reply_text,
            link or "",
            influencer_id
        )
    
    elif action == "auto_hidden":
        return await hide_comment(
            instagram_comment_id,
            influencer_id
        )
    
    elif action in ["pending_review", "flagged_collab", "flagged_manual"]:
        # Don't post anything - just notify
        print(f"⏳ Action '{action}' - waiting for influencer review")
        return True
    
    return False