"""Smart Assist Backend API - Main FastAPI Application."""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime
import sys
import os

# Add the financial-insights-agents to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'financial-insights-agents'))

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Smart Assist API",
    description="Backend API for Smart Assist Chat Interface",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for chat sessions (replace with database in production)
chat_sessions: Dict[str, List[Dict[str, Any]]] = {}


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    session_id: str
    response: str
    timestamp: str


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    message_count: int
    created_at: str
    last_updated: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "Smart Assist API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Process a chat message and return agent response.

    This endpoint handles synchronous chat messages. For streaming responses,
    use the WebSocket endpoint at /ws/chat
    """
    try:
        # Create or retrieve session
        session_id = chat_message.session_id or str(uuid.uuid4())

        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
            logger.info(f"Created new chat session: {session_id}")

        # Store user message
        user_message = {
            "role": "user",
            "content": chat_message.message,
            "timestamp": datetime.utcnow().isoformat()
        }
        chat_sessions[session_id].append(user_message)

        # TODO: Integrate with actual agent system
        # For now, return a mock response
        agent_response = await process_with_agent(chat_message.message, session_id)

        # Store agent response
        assistant_message = {
            "role": "assistant",
            "content": agent_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        chat_sessions[session_id].append(assistant_message)

        logger.info(f"Processed message for session {session_id}")

        return ChatResponse(
            session_id=session_id,
            response=agent_response,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions", response_model=List[SessionInfo])
async def get_sessions():
    """Get all active chat sessions."""
    sessions = []
    for session_id, messages in chat_sessions.items():
        if messages:
            sessions.append(SessionInfo(
                session_id=session_id,
                message_count=len(messages),
                created_at=messages[0]["timestamp"],
                last_updated=messages[-1]["timestamp"]
            ))
    return sessions


@app.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    """Get chat history for a specific session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": chat_sessions[session_id]
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del chat_sessions[session_id]
    logger.info(f"Deleted session: {session_id}")

    return {"message": "Session deleted successfully"}


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming chat responses.

    This allows real-time bidirectional communication and streaming responses.
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for session: {session_id}")

    # Initialize session if it doesn't exist
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")

            # Store user message
            chat_sessions[session_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Process with agent and stream response
            response = await process_with_agent(user_message, session_id)

            # Store agent response
            chat_sessions[session_id].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send response back to client
            await websocket.send_json({
                "type": "message",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })


async def process_with_agent(message: str, session_id: str) -> str:
    """
    Process message with the agent system.

    TODO: Integrate with actual agent orchestration from financial-insights-agents
    This is a placeholder that returns mock responses.
    """
    # Mock response for now
    # In production, this would:
    # 1. Route the query to the appropriate agent (SQL, Analyst, or Expert)
    # 2. Execute agent logic
    # 3. Return formatted response

    if "portfolio" in message.lower():
        return "I can help you analyze your portfolio. The system currently shows you have 3 active portfolios with a total value of $150,000. Would you like me to show you detailed performance metrics?"
    elif "return" in message.lower():
        return "Based on your portfolio data, your year-to-date return is 12.5%, outperforming the S&P 500 by 2.3%. Would you like me to break this down by asset class?"
    elif "risk" in message.lower():
        return "Your portfolio has a beta of 0.95 and a Sharpe ratio of 1.8, indicating good risk-adjusted returns. The current allocation is 60% stocks, 30% bonds, and 10% cash."
    else:
        return f"I understand you're asking about: '{message}'. I'm a financial insights agent that can help you with portfolio analysis, performance metrics, risk assessment, and market comparisons. What would you like to know?"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
