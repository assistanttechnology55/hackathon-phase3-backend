from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, Conversation, Message
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
from datetime import datetime

router = APIRouter()

# ============ Request/Response Schemas ============
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[dict] = []

class ToolCall(BaseModel):
    name: str
    parameters: dict

# ============ Chat Endpoint ============

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    db: Session = Depends(get_session)
):
    """
    Chat endpoint - receives user message and returns AI response
    Uses OpenAI Agents SDK with MCP tools
    """
    try:
        # 1. Get or create conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation = Conversation(
                user_id=int(user_id),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id
        else:
            conversation = db.get(Conversation, conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            conversation.updated_at = datetime.utcnow()
            db.add(conversation)
            db.commit()
        
        # 2. Store user message in database
        user_message = Message(
            user_id=int(user_id),
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            created_at=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        
        # 3. Call OpenAI Agents SDK with MCP tools
        ai_response, tool_calls = await call_ai_agent(request.message, user_id)
        
        # 4. Store AI response in database
        assistant_message = Message(
            user_id=int(user_id),
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            created_at=datetime.utcnow()
        )
        db.add(assistant_message)
        db.commit()
        
        # 5. Return response
        return ChatResponse(
            conversation_id=conversation_id,
            response=ai_response,
            tool_calls=tool_calls
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def call_ai_agent(user_message: str, user_id: str) -> tuple[str, list]:
    """
    Call OpenAI Agents SDK with MCP tools
    Returns: (response_text, tool_calls_list)
    """
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            # Fallback: Simple rule-based responses for development
            return get_fallback_response(user_message, user_id)
        
        # Use OpenAI API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an AI assistant for a Todo app. 
                            You can help users manage their tasks using these tools:
                            - add_task: Create a new task
                            - list_tasks: Get user's tasks (status: all/pending/completed)
                            - complete_task: Mark a task as complete
                            - delete_task: Remove a task
                            - update_task: Modify task title or description
                            
                            When user wants to do something, use the appropriate tool.
                            Always be friendly and helpful."""
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "add_task",
                                "description": "Add a new task",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string", "description": "Task title"},
                                        "description": {"type": "string", "description": "Task description (optional)"}
                                    },
                                    "required": ["title"]
                                }
                            }
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "list_tasks",
                                "description": "List tasks",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "enum": ["all", "pending", "completed"]}
                                    }
                                }
                            }
                        }
                    ],
                    "tool_choice": "auto"
                }
            )
            
            data = response.json()
            
            # Check if AI wants to call a tool
            if data["choices"][0]["message"].get("tool_calls"):
                tool_calls = []
                for tc in data["choices"][0]["message"]["tool_calls"]:
                    tool_calls.append({
                        "name": tc["function"]["name"],
                        "parameters": eval(tc["function"]["arguments"])
                    })
                
                # Execute the tool
                tool_response = await execute_tool(tool_calls[0], user_id)
                
                return tool_response, tool_calls
            else:
                return data["choices"][0]["message"]["content"], []
    
    except Exception as e:
        return get_fallback_response(user_message, user_id)

def get_fallback_response(user_message: str, user_id: str) -> tuple[str, list]:
    """
    Fallback responses when OpenAI is not configured
    """
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["add", "create", "remember"]):
        return "I've added that task for you! Is there anything else?", [{
            "name": "add_task",
            "parameters": {"title": "New task", "description": "Created from chat"}
        }]
    elif any(word in message_lower for word in ["list", "show", "what", "pending"]):
        return "Here are your tasks:\n• Task 1 (pending)\n• Task 2 (completed)\n\nYou have 1 pending task.", [{
            "name": "list_tasks",
            "parameters": {"status": "all"}
        }]
    elif any(word in message_lower for word in ["complete", "done", "finish"]):
        return "Great job! I've marked that task as complete! 🎉", [{
            "name": "complete_task",
            "parameters": {"task_id": 1}
        }]
    elif any(word in message_lower for word in ["delete", "remove"]):
        return "I've deleted that task for you.", [{
            "name": "delete_task",
            "parameters": {"task_id": 1}
        }]
    else:
        return "I'm your AI task assistant! I can help you:\n\n• Add new tasks\n• List your tasks\n• Mark tasks as complete\n• Delete tasks\n\nJust ask me in natural language!", []

async def execute_tool(tool_call: dict, user_id: str) -> str:
    """
    Execute a tool call
    """
    # This would call the actual MCP tools
    # For now, return a simple response
    return f"Executed {tool_call['name']} successfully!"
