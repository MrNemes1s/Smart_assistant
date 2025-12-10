# Smart Assist Backend API

FastAPI backend for the Smart Assist chat interface, providing REST and WebSocket endpoints for the financial insights agent system.

## Features

- REST API for synchronous chat messages
- WebSocket support for streaming responses
- Session management
- Chat history storage
- CORS enabled for frontend integration
- Health check endpoints

## API Endpoints

### REST Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check endpoint
- `POST /api/chat` - Send a chat message (synchronous)
- `GET /api/sessions` - List all active sessions
- `GET /api/sessions/{session_id}` - Get chat history for a session
- `DELETE /api/sessions/{session_id}` - Delete a session

### WebSocket Endpoint

- `WS /ws/chat/{session_id}` - WebSocket connection for streaming chat

## Setup

### Local Development

1. **Install dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the server:**

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Send a Chat Message (REST)

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my portfolio performance?"}'
```

### Get Sessions

```bash
curl "http://localhost:8000/api/sessions"
```

### WebSocket Example (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/session-123');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Show me my portfolio returns"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data.content);
};
```

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## Integration with Agent System

The backend is designed to integrate with the `financial-insights-agents` system. The `process_with_agent()` function in `main.py` is the integration point where agent orchestration logic should be added.

## Development

### Adding New Endpoints

1. Add route handlers in `main.py`
2. Define Pydantic models for request/response
3. Update API documentation

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Deployment

See the `/docs` folder for detailed Azure deployment instructions.

## Security Considerations

- CORS is configured for development (localhost origins)
- In production, update CORS origins to your domain
- Add authentication/authorization as needed
- Use HTTPS in production
- Implement rate limiting
- Add input validation and sanitization

## Next Steps

1. Integrate with actual agent orchestration system
2. Add authentication (JWT tokens)
3. Implement persistent storage (database)
4. Add rate limiting
5. Implement agent streaming responses
6. Add monitoring and logging
