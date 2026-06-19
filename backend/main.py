import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db.supabase_client import supabase
from models.ollama_client import model
from api.webhooks import router as webhook_router
from api.rules import router as rules_router
from api.dashboard import router as dashboard_router  # ← ADD THIS

load_dotenv()

app = FastAPI(
    title="ReplyPilot AI",
    description="Smart Comment Automation for Influencers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(rules_router)
app.include_router(dashboard_router)  # ← ADD THIS

@app.get("/")
async def root():
    return {"status": "ReplyPilot AI is running 🚀", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    try:
        supabase.table("influencers").select("id").limit(1).execute()
        db_status = "connected ✅"
    except Exception as e:
        db_status = f"error ❌: {str(e)}"
    try:
        response = model.invoke("Say OK")
        ollama_status = "connected ✅"
    except Exception as e:
        ollama_status = f"error ❌: {str(e)}"
    return {
        "supabase": db_status,
        "ollama": ollama_status,
        "server": "running ✅"
    }