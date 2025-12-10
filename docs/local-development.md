# Local Development Guide - Smart Assist

Complete guide for setting up and running Smart Assist locally.

## Quick Start

```bash
# 1. Start Backend
cd backend
pip install -r requirements.txt
python main.py

# 2. Start Frontend (in new terminal)
cd frontend
npm install
npm run dev

# Access at: http://localhost:3000
```

## Prerequisites

### Required Software

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Git**: [Download Git](https://git-scm.com/)

### Optional (for full agent functionality)

- **MSSQL Server**: Local or Azure SQL
- **Docker**: For containerized development
- **Azure CLI**: For cloud integration

## Backend Setup

### 1. Install Python Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Minimal `.env` for local development:
```env
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
DEBUG=true
```

### 3. Run Backend Server

```bash
# Run with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### 4. Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# View API docs
# Open in browser: http://localhost:8000/docs
```

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend

# Install packages
npm install

# Or using yarn
yarn install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Should contain:
# VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
# Start Vite dev server
npm run dev

# Or using yarn
yarn dev
```

Frontend will be available at: `http://localhost:3000`

### 4. Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Database Setup (Optional)

### Option 1: Docker MSSQL

```bash
# Pull MSSQL Docker image
docker pull mcr.microsoft.com/mssql/server:2022-latest

# Run MSSQL container
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=YourStrong@Password" \
   -p 1433:1433 --name mssql-server \
   -d mcr.microsoft.com/mssql/server:2022-latest

# Wait for container to start
docker logs mssql-server

# Create database
docker exec -it mssql-server /opt/mssql-tools/bin/sqlcmd \
   -S localhost -U sa -P "YourStrong@Password" \
   -Q "CREATE DATABASE financial_insights_db"
```

### Option 2: Local MSSQL Installation

1. Download and install [SQL Server](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
2. Use SQL Server Management Studio or Azure Data Studio
3. Create database: `financial_insights_db`
4. Run schema scripts:

```bash
cd financial-insights-agents/database/sample_schema

sqlcmd -S localhost -U sa -P YourPassword \
  -d financial_insights_db \
  -i create_tables.sql

sqlcmd -S localhost -U sa -P YourPassword \
  -d financial_insights_db \
  -i seed_data.sql
```

### Update Backend Configuration

Add to `backend/.env`:
```env
MSSQL_SERVER=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=financial_insights_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourStrong@Password
```

## Full Stack Development

### Using Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - ENVIRONMENT=development
    volumes:
      - ./backend:/app
    depends_on:
      - database

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  database:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - MSSQL_SA_PASSWORD=YourStrong@Password
    ports:
      - "1433:1433"
    volumes:
      - mssql-data:/var/opt/mssql

volumes:
  mssql-data:
```

Run with:
```bash
docker-compose up
```

## Development Workflow

### Backend Development

1. **Make Changes**: Edit Python files in `backend/`
2. **Auto-Reload**: Server automatically restarts
3. **Test**: Use curl or Swagger UI at `/docs`
4. **Debug**: Check console output

### Frontend Development

1. **Make Changes**: Edit React files in `frontend/src/`
2. **Hot Reload**: Browser automatically updates
3. **Test**: Interact with UI
4. **Debug**: Use browser DevTools (F12)

### Testing API Integration

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Test
curl http://localhost:8000/health
curl http://localhost:3000
```

## Debugging

### Backend Debugging

#### Using VS Code

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

#### Using Print Statements

```python
# In main.py
print(f"Received message: {chat_message.message}")
print(f"Session ID: {session_id}")
```

#### Using Python Debugger

```python
import pdb; pdb.set_trace()
```

### Frontend Debugging

#### Browser DevTools

1. Open DevTools (F12)
2. Console tab: View logs and errors
3. Network tab: Inspect API calls
4. React DevTools: Inspect component state

#### VS Code Debugging

Install "Debugger for Chrome" extension, then create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

#### Console Logging

```typescript
console.log('Message sent:', input);
console.log('Response received:', response.data);
```

## Common Issues

### Issue 1: Port Already in Use

**Backend (Port 8000)**:
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

**Frontend (Port 3000)**:
```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>

# Or Vite will auto-suggest different port
```

### Issue 2: CORS Errors

Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: Module Not Found

**Backend**:
```bash
pip install -r requirements.txt
# Or for specific package:
pip install fastapi uvicorn
```

**Frontend**:
```bash
npm install
# Or for specific package:
npm install axios lucide-react
```

### Issue 4: Database Connection Failed

Check:
1. Database is running: `docker ps` or check MSSQL service
2. Credentials are correct in `.env`
3. Firewall allows connection
4. Connection string format is correct

Test connection:
```bash
sqlcmd -S localhost -U sa -P YourPassword -Q "SELECT 1"
```

## Testing

### Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=.
```

### Frontend Tests

```bash
cd frontend

# Install test dependencies
npm install --save-dev vitest @testing-library/react

# Run tests
npm test
```

## Code Quality

### Backend Linting

```bash
# Install tools
pip install black flake8 mypy

# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

### Frontend Linting

```bash
# Lint
npm run lint

# Format with Prettier (if configured)
npm run format
```

## Environment Variables Reference

### Backend (.env)

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Environment
ENVIRONMENT=development
DEBUG=true

# Database (optional for basic functionality)
MSSQL_SERVER=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=financial_insights_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPassword

# Azure (optional for full agent functionality)
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key
```

### Frontend (.env)

```env
# Backend API URL
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
Smart_assitant/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── App.css         # Styles
│   │   ├── main.tsx        # Entry point
│   │   └── index.css       # Global styles
│   ├── package.json        # Node dependencies
│   ├── vite.config.ts      # Vite configuration
│   ├── .env                # Environment variables
│   └── README.md
│
├── financial-insights-agents/  # Agent system
│   ├── agents/
│   ├── mcp_servers/
│   ├── core/
│   └── database/
│
└── docs/                   # Documentation
    ├── azure-deployment-guide.md
    └── local-development.md
```

## Next Steps

1. Explore the API documentation: `http://localhost:8000/docs`
2. Test the chat interface
3. Review agent system in `financial-insights-agents/`
4. Customize UI in `frontend/src/`
5. Add new API endpoints in `backend/main.py`

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)

---

**Happy Coding!**
