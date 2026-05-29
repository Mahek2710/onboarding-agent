import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SLACK_WEBHOOK_GENERAL = os.getenv("SLACK_WEBHOOK_GENERAL")
SLACK_WEBHOOK_HR = os.getenv("SLACK_WEBHOOK_HR")

def send_welcome_message(name: str, role: str, experience: str, tech_stack: str):
    """Naye employee ka welcome message #general mein bhejo"""
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Welcome to the team, {name}!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Role:*\n{role.capitalize()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Experience:*\n{experience.capitalize()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Tech Stack:*\n{tech_stack.capitalize()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Joined:*\n{datetime.now().strftime('%d %b %Y')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Please give a warm welcome to *{name}* who is joining as a *{experience} {role} developer*! :wave:"
                }
            }
        ]
    }
    
    response = requests.post(SLACK_WEBHOOK_GENERAL, json=message)
    
    if response.status_code == 200:
        print(f"Welcome message sent for {name}")
        return True
    else:
        print(f"Slack error: {response.text}")
        return False

def send_hr_completion_report(name: str, role: str, experience: str, 
                               tech_stack: str, checklist: list):
    """Onboarding complete hone pe HR ko structured report bhejo"""
    
    completed_tasks = [t for t in checklist if t["is_completed"]]
    pending_tasks = [t for t in checklist if not t["is_completed"]]
    
    total = len(checklist)
    done = len(completed_tasks)
    score = int((done / total) * 100) if total > 0 else 0
    
    completed_text = "\n".join([f"✅ {t['task_name']}" for t in completed_tasks])
    pending_text = "\n".join([f"⏳ {t['task_name']}" for t in pending_tasks]) if pending_tasks else "None"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Onboarding Completion Report"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Employee:*\n{name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Role:*\n{experience.capitalize()} {role.capitalize()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Tech Stack:*\n{tech_stack.capitalize()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Completion Score:*\n{score}% ({done}/{total})"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Completed Tasks:*\n{completed_text}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Pending Tasks:*\n{pending_text}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Report generated at {datetime.now().strftime('%d %b %Y, %H:%M IST')}"
                    }
                ]
            }
        ]
    }
    
    response = requests.post(SLACK_WEBHOOK_HR, json=message)
    
    if response.status_code == 200:
        print(f"HR report sent for {name}")
        return True
    else:
        print(f"Slack HR error: {response.text}")
        return False

if __name__ == "__main__":
    # Test karo
    send_welcome_message("Riya", "backend", "intern", "Node.js")
    print("Test message sent — Slack check karo!")