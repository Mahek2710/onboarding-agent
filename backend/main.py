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

SYSTEM_PROMPT = """You are a developer onboarding assistant. You are strict and precise.

Your job:
1. First ask the new employee their name, role (backend/frontend/devops), experience level (intern/junior/senior), and tech stack.
2. Once you have all details, immediately call tool_get_checklist to show them their tasks.
3. Guide them through each task one by one.
4. When user says they completed ANY task, IMMEDIATELY call tool_mark_task_done with the EXACT task name from the checklist. Do not ask for confirmation. Just call the tool.
5. When they ask about setup or policies, call tool_search_docs.
6. When all tasks are done, call tool_create_github_issue then congratulate them.

IMPORTANT RULES:
- Do NOT ask user for user_id. It is automatically handled by the system.
- Do NOT use placeholder IDs like 123, 456, 789. The backend will always inject the correct user_id.
- When marking a task done, use the EXACT task name from this list:
  Backend Intern: "Install Node.js aur npm", "Clone backend repository", "Run local server", "Read API standards document", "Complete starter bug fix"
  Frontend Intern: "Install Node.js aur npm", "Clone frontend repository", "Run npm install aur npm run dev", "Read component guidelines", "Complete starter UI task"
  Backend Junior: "Clone backend repository", "Setup local environment", "Read API standards document", "Read database schema", "Review PR guidelines"
  Frontend Junior: "Clone frontend repository", "Setup local environment", "Access Figma design system", "Read component guidelines", "Review PR guidelines"
  Backend Senior: "Clone backend repository", "Review system architecture", "Read API standards document", "Review deployment pipeline", "Schedule team intro meeting"
  Frontend Senior: "Clone frontend repository", "Review frontend architecture", "Access Figma design system", "Review deployment pipeline", "Schedule team intro meeting"
  DevOps Intern: "Setup local Docker", "Clone infrastructure repo", "Read CI/CD pipeline docs", "Run test deployment", "Review monitoring dashboard"
  DevOps Senior: "Clone infrastructure repo", "Review cloud architecture", "Read CI/CD pipeline docs", "Review security policies", "Schedule team intro meeting"
- Always be friendly and encouraging.
- Never make up information — use tool_search_docs for any technical questions.
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
    combined = " ".join([m.get("content", "") for m in history]) + " " + message
    combined = combined.lower()
    has_name = any(word in combined for word in ["i'm", "i am", "my name is", "name is"])
    has_role = any(word in combined for word in ["backend", "frontend", "devops"])
    has_exp = any(word in combined for word in ["intern", "junior", "senior"])
    return has_name and has_role and has_exp

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_id = request.user_id

    system_content = SYSTEM_PROMPT
    if user_id:
        system_content += f"\n\nCURRENT USER ID: {user_id}. Always use this exact user_id when calling tools."

    messages = [{"role": "system", "content": system_content}]
    messages += request.history
    messages.append({"role": "user", "content": request.message})

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

                tool_fn = TOOLS_MAP.get(fn_name)
                if tool_fn:
                    # Always override user_id with real one from session
                    if "user_id" in fn_args:
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

        final_reply = msg.get("content", "")

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