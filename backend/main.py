import json
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Optional
from slack_helper import send_welcome_message, send_hr_completion_report
from email_helper import send_hr_email

from database import init_db, create_user, get_user, get_checklist, is_onboarding_complete
from agent_tools import TOOLS_DEFINITION, TOOLS_MAP

load_dotenv()

app = FastAPI(title="Onboarding Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemma-3-27b-it"

SYSTEM_PROMPT = """You are a friendly developer onboarding assistant.

Your job:
1. First ask the new employee their name, role (backend/frontend/devops), experience level (intern/junior/senior), and tech stack.
2. Once you have all details, tell them their onboarding checklist.
3. Guide them step by step through each task.
4. When they say they completed a task, use tool_mark_task_done to update it.
5. When they ask about setup or policies, use tool_search_docs to find answers from company documents.
6. If you answer something not in documents, save it using tool_save_faq.
7. When all tasks are done, congratulate them.

Rules:
- Always be friendly and encouraging.
- Never make up information not in company documents.
- Always use tools when available instead of guessing.
- Speak in simple English."""

class ChatRequest(BaseModel):
    message: str
    history: list = []
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    user_id: Optional[int] = None
    checklist: list = []

def call_llm(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS_DEFINITION,
        "tool_choice": "auto"
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=body
    )
    return response.json()

def extract_user_info(message: str, history: list):
    """Simple check — kya user ne apna intro diya hai"""
    combined = " ".join([m.get("content", "") for m in history]) + " " + message
    combined = combined.lower()
    
    has_name = any(word in combined for word in ["i'm", "i am", "my name is", "name is"])
    has_role = any(word in combined for word in ["backend", "frontend", "devops"])
    has_exp = any(word in combined for word in ["intern", "junior", "senior"])
    
    return has_name and has_role and has_exp

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += request.history
    messages.append({"role": "user", "content": request.message})
    
    user_id = request.user_id
    max_loops = 5

    for _ in range(max_loops):
        response = call_llm(messages)
        
        if "error" in response:
            return ChatResponse(reply=f"Error: {response['error']}", user_id=user_id)
        
        choice = response["choices"][0]
        msg = choice["message"]
        finish_reason = choice["finish_reason"]

        if finish_reason == "tool_calls" or msg.get("tool_calls"):
            messages.append(msg)
            
            for tool_call in msg["tool_calls"]:
                fn_name = tool_call["function"]["name"]
                fn_args = json.loads(tool_call["function"]["arguments"])
                
                print(f"Tool called: {fn_name} with {fn_args}")
                
                # User create karna agar pehli baar hai
                if fn_name == "tool_mark_task_done" and user_id is None:
                    pass
                
                tool_fn = TOOLS_MAP.get(fn_name)
                if tool_fn:
                    if "user_id" in fn_args and fn_args["user_id"] is None:
                        fn_args["user_id"] = user_id
                    result = tool_fn(**fn_args)
                else:
                    result = f"Tool {fn_name} not found"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(result)
                })
            continue

        # Final reply
        final_reply = msg.get("content", "")
        
        # Agar user ne intro diya aur user_id nahi hai toh create karo
        if user_id is None and extract_user_info(request.message, request.history):
            combined = " ".join([m.get("content", "") for m in messages]).lower()
            
            name = "New Employee"
            role = "backend"
            experience = "intern"
            tech_stack = "general"
            
            for word in ["backend", "frontend", "devops"]:
                if word in combined:
                    role = word
                    break
            
            for word in ["intern", "junior", "senior"]:
                if word in combined:
                    experience = word
                    break
            
            for word in ["node", "react", "python", "java", "javascript"]:
                if word in combined:
                    tech_stack = word
                    break

            words = request.message.split()
            for i, word in enumerate(words):
                if word.lower() in ["i'm", "am", "is"] and i + 1 < len(words):
                    name = words[i + 1].capitalize()
                    break

            user_id = create_user(name, role, experience, tech_stack)
            print(f"New user created: {name} | {role} | {experience} | ID: {user_id}")
            # Slack welcome message bhejo
            send_welcome_message(name, role, experience, tech_stack)

        checklist = get_checklist(user_id) if user_id else []
        
        return ChatResponse(
            reply=final_reply,
            user_id=user_id,
            checklist=checklist
        )

    return ChatResponse(reply="Kuch problem aayi, dobara try karo.", user_id=user_id)

@app.get("/checklist/{user_id}")
async def get_user_checklist(user_id: int):
    checklist = get_checklist(user_id)
    user = get_user(user_id)
    return {"user": user, "checklist": checklist}

@app.get("/")
async def root():
    return {"message": "Onboarding Agent is running!"}