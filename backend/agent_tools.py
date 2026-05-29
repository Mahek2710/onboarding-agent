import json
import requests as req
import os
from database import get_checklist, mark_task_done, is_onboarding_complete, get_user
from ingest import search_docs, get_chroma_collection

def tool_search_docs(query: str) -> str:
    """ChromaDB se relevant documents search karo"""
    result = search_docs(query)
    return result

def tool_mark_task_done(user_id: int, task_name: str) -> str:
    """Checklist mein ek task complete mark karo"""
    mark_task_done(user_id, task_name)
    checklist = get_checklist(user_id)
    
    done = sum(1 for t in checklist if t["is_completed"])
    total = len(checklist)
    
    if is_onboarding_complete(user_id):
        return f"Task '{task_name}' complete! Onboarding poora ho gaya ({done}/{total}). HR report trigger ho rahi hai."
    
    remaining = [t["task_name"] for t in checklist if not t["is_completed"]]
    return f"Task '{task_name}' complete! Progress: {done}/{total}. Baaki tasks: {', '.join(remaining)}"

def tool_get_checklist(user_id: int) -> str:
    """User ka current checklist return karo"""
    checklist = get_checklist(user_id)
    if not checklist:
        return "Koi checklist nahi mili."
    
    output = "Current checklist:\n"
    for task in checklist:
        status = "✓" if task["is_completed"] else "○"
        output += f"  {status} {task['task_name']}\n"
    return output

def tool_save_faq(question: str, answer: str) -> str:
    """Naya FAQ ChromaDB mein save karo"""
    collection = get_chroma_collection()
    
    existing = collection.get(where={"source": "faq"})
    faq_count = len(existing["ids"]) if existing["ids"] else 0
    
    doc_id = f"faq_{faq_count + 1}"
    collection.add(
        ids=[doc_id],
        documents=[f"Q: {question}\nA: {answer}"],
        metadatas=[{"source": "faq"}]
    )
    return f"FAQ saved: '{question}'"

# LLM ko yeh tools JSON format mein denge
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "tool_create_github_issue",
            "description": "Jab onboarding complete ho tab naye employee ke liye GitHub starter issue create karo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Employee ka naam"
                    },
                    "role": {
                        "type": "string",
                        "description": "Employee ka role"
                    },
                    "tech_stack": {
                        "type": "string",
                        "description": "Employee ka tech stack"
                    }
                },
                "required": ["name", "role", "tech_stack"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_search_docs",
            "description": "Company ke internal documents aur FAQs se relevant information search karo. Jab user koi setup ya policy related sawaal pooche tab use karo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query — jo information chahiye"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_mark_task_done",
            "description": "Jab user bole ki usne koi task complete kar liya tab is tool se checklist update karo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "User ka ID"
                    },
                    "task_name": {
                        "type": "string",
                        "description": "Jo task complete hua uska exact naam"
                    }
                },
                "required": ["user_id", "task_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_checklist",
            "description": "User ka poora checklist dekho — kaunse tasks bache hain kaunse complete hain.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "User ka ID"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_save_faq",
            "description": "Jab user koi aisa sawaal pooche jo documents mein nahi hai aur agent ne jawab diya ho, tab us Q&A ko future ke liye save karo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "User ka sawaal"
                    },
                    "answer": {
                        "type": "string",
                        "description": "Agent ka jawab"
                    }
                },
                "required": ["question", "answer"]
            }
        }
    }
]


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

def tool_create_github_issue(name: str, role: str, tech_stack: str) -> str:
    """Naye employee ke liye GitHub starter issue create karo"""
    
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return "GitHub credentials missing in .env"
    
    title = f"Onboarding Starter Task: {name}"
    
    body = f"""## Welcome {name}!

This is your first starter task as a **{role} developer** working with **{tech_stack}**.

### Your Task:
- [ ] Read the codebase README
- [ ] Set up your local development environment
- [ ] Make a small improvement or fix a typo in documentation
- [ ] Submit your first Pull Request

### Resources:
- Ask your team lead for repository access
- Check the onboarding documentation in the wiki
- Reach out on Slack if you need help

**Good luck on your onboarding journey!**
"""
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "title": title,
        "body": body,
        "labels": ["onboarding", "good first issue"]
    }
    
    response = req.post(
        f"https://api.github.com/repos/{GITHUB_REPO}/issues",
        headers=headers,
        json=data
    )
    
    if response.status_code == 201:
        issue_url = response.json()["html_url"]
        return f"GitHub issue created: {issue_url}"
    else:
        return f"GitHub error: {response.json()}"

TOOLS_MAP = {
    "tool_search_docs": tool_search_docs,
    "tool_mark_task_done": tool_mark_task_done,
    "tool_get_checklist": tool_get_checklist,
    "tool_save_faq": tool_save_faq,
    "tool_create_github_issue": tool_create_github_issue,  # yeh add karo
}