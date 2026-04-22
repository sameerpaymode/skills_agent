from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, AsyncGenerator
import asyncio
import json
from agent_framework import Message
from agent import agent

app = FastAPI(title="AI Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Serve PDFs from saved_docs/
app.mount("/saved_docs", StaticFiles(directory="saved_docs"), name="saved_docs")

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    text: str
    skill_name: str = None


async def stream_chat(messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
    """
    Stream chat responses with skill tracking.
    Yields JSON lines with the format:
    {"type": "text", "content": "..."}
    {"type": "skill", "skill_name": "..."}
    {"type": "done"}
    """
    
    # Convert ChatMessage to agent framework Message
    agent_messages = [Message(msg.role, [msg.content]) for msg in messages]
    
    text_buffer = ""
    skill_buffer = ""
    
    async for update in agent.run(agent_messages, stream=True):
        if update.contents:
            content = update.contents[0]
            
            if content.type == "function_call":
                try:
                    skill_buffer += content.arguments
                    skill_data = json.loads(skill_buffer)
                    skill_name = skill_data.get("skill_name", "Unknown Skill")
                    
                    # Send skill notification
                    yield json.dumps({
                        "type": "skill",
                        "skill_name": skill_name
                    }) + "\n"
                    
                except json.JSONDecodeError:
                    # Still parsing the JSON
                    pass
                except Exception as e:
                    print(f"Error parsing skill: {e}")
            
            elif content.type == "function_result":
                # Skill completed, reset buffer
                skill_buffer = ""
        
        if update.text:
            # Send text content as it streams
            yield json.dumps({
                "type": "text",
                "content": update.text
            }) + "\n"
            text_buffer += update.text
    
    # Signal completion
    yield json.dumps({
        "type": "done",
        "final_text": text_buffer
    }) + "\n"


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Stream chat endpoint.
    Returns Server-Sent Events (SSE) style streaming response.
    """
    
    try:
        return StreamingResponse(
            stream_chat(request.messages),
            media_type="application/x-ndjson",
            headers={"Cache-Control": "no-cache"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)