# Smart Assist

A modern web application for financial insights powered by AI agents. Smart Assist provides an intuitive chat interface to analyze portfolios, calculate returns, assess risk, and get expert financial advice.

## Overview

Smart Assist is a full-stack application that combines:
- **Frontend**: React + TypeScript chat interface
- **Backend**: FastAPI REST API with WebSocket support
- **Agent System**: Multi-agent analysis engine
- **Database**: MSSQL for financial data storage

## Quick Start

### Local Development

```bash
# 1. Start Backend
cd backend
pip install -r requirements.txt
python main.py

# 2. Start Frontend (new terminal)
cd frontend
npm install
npm run dev

# 3. Open browser
# Navigate to: http://localhost:3000
```

## Project Structure

```
Smart_assitant/
├── backend/                    # FastAPI Backend
│   ├── main.py                # API application
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment template
│   └── README.md             # Backend documentation
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.tsx           # Main component
│   │   ├── App.css           # Styles
│   │   └── main.tsx          # Entry point
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   └── README.md             # Frontend documentation
│
├── financial-insights-agents/  # Agent System
│   ├── agents/               # AI agents
│   ├── mcp_servers/          # MCP servers
│   ├── core/                 # Core utilities
│   ├── database/             # Database schemas
│   └── README.md             # Agent documentation
│
└── docs/                       # Documentation
    ├── azure-deployment-guide.md    # Azure setup
    └── local-development.md         # Local dev guide
```

## Features

### Chat Interface
- Real-time messaging with AI agents
- Session management
- Message history
- Beautiful, responsive UI
- Mobile-friendly design

### Backend API
- REST endpoints for chat
- WebSocket support for streaming
- Session persistence
- Health monitoring
- CORS enabled

### Agent System
- **SQL Agent**: Natural language to SQL queries
- **Data Analyst Agent**: Statistical analysis
- **Domain Expert Agent**: Domain insights
- Multi-agent orchestration

### Financial Analysis
- Portfolio performance tracking
- Risk assessment
- Return calculations
- Market comparisons
- Sector analysis

## Documentation

### Getting Started
- [Local Development Guide](docs/local-development.md) - Setup and run locally
- [Backend README](backend/README.md) - Backend API documentation
- [Frontend README](frontend/README.md) - Frontend documentation

### Deployment
- [Azure Deployment Guide](docs/azure-deployment-guide.md) - Complete Azure setup
  - Prerequisites and requirements
  - Step-by-step deployment
  - Debugging and troubleshooting
  - Cost optimization
  - Security best practices

### Agent System
- [Analysis Agents](financial-insights-agents/README.md) - Agent architecture

## Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Axios** - HTTP client
- **Lucide React** - Icons

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time communication
- **Pydantic** - Data validation

### Agent System
- **Microsoft Agent Framework** - Agent orchestration
- **Claude via Azure AI Foundry** - LLM
- **MSSQL** - Database
- **MCP** - Model Context Protocol

### Infrastructure
- **Azure App Service** - Backend hosting
- **Azure Static Web Apps** - Frontend hosting
- **Azure SQL Database** - Data storage
- **Azure AI Foundry** - AI/ML services
- **Application Insights** - Monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Browser                         │
│                  (React Frontend)                        │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/WebSocket
                  ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend                             │
│          (REST API + WebSocket)                          │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴──────────┬────────────────┐
        ▼                    ▼                 ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  SQL Agent   │   │Data Analyst  │   │Domain Expert │
│              │   │    Agent     │   │    Agent     │
└──────┬───────┘   └──────┬───────┘   └──────────────┘
       │                  │
       ▼                  ▼
┌──────────────────────────────────┐
│      MSSQL Database              │
│   (Financial Data Storage)       │
└──────────────────────────────────┘
```

## API Endpoints

### REST API

- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /api/chat` - Send chat message
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session history
- `DELETE /api/sessions/{id}` - Delete session

### WebSocket

- `WS /ws/chat/{session_id}` - Real-time chat

API documentation available at: `http://localhost:8000/docs`

## Example Queries

Ask Smart Assist questions like:

- "What is my portfolio's total return over the last year?"
- "Calculate the Sharpe ratio for my holdings vs S&P 500"
- "Show me the top 5 performing stocks in my portfolio"
- "What is my portfolio's risk exposure by sector?"
- "Compare my returns against market benchmarks"

## Setup Instructions

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Git**

### Optional
- **Azure Account** (for deployment)
- **MSSQL Server** (for full agent functionality)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
python main.py
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env (default points to localhost:8000)

# Run development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

### Database Setup (Optional)

For full agent functionality with real financial data:

```bash
# Using Docker
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=YourStrong@Password" \
   -p 1433:1433 --name mssql-server \
   -d mcr.microsoft.com/mssql/server:2022-latest

# Create database and load schema
cd financial-insights-agents/database/sample_schema
sqlcmd -S localhost -U sa -P YourPassword -i create_tables.sql
sqlcmd -S localhost -U sa -P YourPassword -i seed_data.sql
```

## Deployment

### Azure Deployment

Complete deployment instructions available in [Azure Deployment Guide](docs/azure-deployment-guide.md)

Quick overview:
1. Create Azure resources (App Service, Static Web App, SQL Database)
2. Deploy backend to App Service
3. Deploy frontend to Static Web Apps
4. Configure environment variables
5. Set up monitoring

### Local Testing

```bash
# Test backend
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test frontend
# Open browser: http://localhost:3000
```

## Configuration

### Backend Environment Variables

Create `backend/.env`:
```env
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
DEBUG=true

# Optional: Database
MSSQL_SERVER=localhost
MSSQL_DATABASE=financial_insights_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPassword

# Optional: Azure AI
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string
AZURE_OPENAI_ENDPOINT=your-endpoint
```

### Frontend Environment Variables

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py  # Auto-reload enabled
```

Edit files in `backend/` - server auto-restarts

### Frontend Development

```bash
cd frontend
npm run dev  # Hot reload enabled
```

Edit files in `frontend/src/` - browser auto-updates

### Code Quality

```bash
# Backend
cd backend
black .              # Format
flake8 .            # Lint
mypy .              # Type check

# Frontend
cd frontend
npm run lint        # ESLint
npm run build       # Type check
```

## Debugging

### Backend Debugging
- Check logs in console
- Use Swagger UI: `http://localhost:8000/docs`
- Enable debug mode in `.env`

### Frontend Debugging
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls
- Use React DevTools extension

### Common Issues

See [Local Development Guide](docs/local-development.md#common-issues) for solutions to:
- Port conflicts
- CORS errors
- Module not found
- Database connection issues

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Guidelines
- Use type hints (Python) and TypeScript
- Add tests for new features
- Update documentation
- Follow existing code style
- Keep commits atomic

## Security

- Never commit `.env` files
- Use strong passwords
- Enable HTTPS in production
- Implement authentication
- Regular dependency updates
- Follow security best practices

## Performance

- Backend uses async/await for concurrency
- Frontend implements lazy loading
- Database uses connection pooling
- Caching for frequently accessed data
- Optimized bundle size

## Monitoring

### Local Development
- Backend logs to console
- Frontend uses browser console
- API docs at `/docs`

### Production
- Application Insights for telemetry
- Azure Monitor for infrastructure
- Custom logging
- Performance metrics
- Error tracking

## Roadmap

### Current Features
- ✅ Chat interface
- ✅ Session management
- ✅ REST API
- ✅ WebSocket support
- ✅ Basic agent responses

### Upcoming Features
- 🚧 Full agent integration
- 🚧 Authentication
- 🚧 User profiles
- 🚧 Chart visualizations
- 🚧 Export functionality
- 🚧 Advanced analytics

### Future Plans
- 📋 Real-time collaboration
- 📋 Mobile apps
- 📋 Voice interface
- 📋 Custom dashboards
- 📋 Advanced reporting

## Support

### Documentation
- [Local Development Guide](docs/local-development.md)
- [Azure Deployment Guide](docs/azure-deployment-guide.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

### Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Azure Documentation](https://docs.microsoft.com/azure)
- [Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-studio)

### Getting Help
- Check documentation
- Review issues
- Read code comments
- Test with example queries

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Microsoft Agent Framework
- Anthropic Claude
- FastAPI framework
- React community
- Azure services

---

**Version**: 1.0.0
**Status**: Active Development
**Last Updated**: December 2025

**Built with ❤️ for financial insights**
