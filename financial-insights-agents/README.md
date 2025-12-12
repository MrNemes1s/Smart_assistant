# Multi-Agent Analysis System

A production-ready multi-agent system for data analysis using Microsoft Agent Framework, Claude via Azure AI Foundry, and MSSQL.

## Architecture

```
User → FastAPI REST API → Agent Hub (Orchestrator)
                             ├─→ SQL Agent (MCP → MSSQL)
                             ├─→ Data Analyst Agent (Code Interpreter)
                             └─→ Domain Expert Agent (Domain Knowledge)
```

## Features

### Completed (Phase 1 & 2)
✅ Project structure and configuration
✅ Core utilities (config, logging, exceptions)
✅ Sample financial database schema (portfolios, holdings, transactions, prices, benchmarks)
✅ MSSQL MCP Server with connection pooling
✅ MCP Client for agent communication
✅ 7 database tools (execute_query, get_schema, get_sample, validate, etc.)

### In Progress (Phase 3)
🚧 Base Agent Class with Azure AI Foundry integration
🚧 SQL Agent (Natural language to SQL)
🚧 Data Analyst Agent (Statistical analysis + charts)
🚧 Domain Expert Agent (Domain metrics + knowledge base)

### Planned (Phase 4-7)
📋 Orchestration hub and router
📋 FastAPI REST API with WebSocket streaming
📋 Azure AI Foundry deployment
📋 Docker containerization
📋 Testing suite

## Technology Stack

- **Framework**: Microsoft Agent Framework (Python SDK)
- **LLM**: Claude 3.5 Sonnet/Opus via Azure AI Foundry
- **Database**: MSSQL with SQLAlchemy connection pooling
- **MCP**: Model Context Protocol for database access
- **API**: FastAPI + WebSockets (upcoming)
- **Data**: Pandas, NumPy, SciPy, Matplotlib
- **Infrastructure**: Docker, Azure Container Instances, Azure App Service

## Project Structure

```
financial-insights-agents/
├── agents/                      # Agent implementations
│   ├── sql_agent/              # SQL query generation agent
│   ├── data_analyst_agent/     # Statistical analysis agent
│   └── domain_expert_agent/    # Domain expert
├── orchestration/               # Agent coordination
├── mcp_servers/                 # MCP server implementations
│   ├── mssql_server/           # MSSQL MCP server
│   │   ├── server.py           # ✅ MCP server with 7 tools
│   │   ├── connection_pool.py  # ✅ SQLAlchemy pooling
│   │   └── requirements.txt    # ✅ Server dependencies
│   └── mcp_client.py           # ✅ Client for agents
├── tools/                       # Shared tools
│   ├── database/               # Database utilities
│   ├── analytics/              # Analysis tools
│   ├── financial/              # Financial calculations
│   └── visualization/          # Chart generation
├── core/                        # Core infrastructure
│   ├── config.py               # ✅ Configuration management
│   ├── exceptions.py           # ✅ Custom exceptions
│   └── logging.py              # ✅ Structured logging
├── api/                         # REST API (upcoming)
├── deployment/                  # Deployment scripts
├── database/                    # Database schemas
│   └── sample_schema/
│       ├── create_tables.sql   # ✅ Financial DB schema
│       └── seed_data.sql       # ✅ Sample data
├── tests/                       # Test suite
├── docs/                        # Documentation
├── .env.example                 # ✅ Environment template
├── pyproject.toml               # ✅ Dependencies
└── README.md                    # ✅ This file
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- MSSQL Server (local or Azure SQL)
- Azure AI Foundry account (for Claude models)
- uv or pip for package management

### 1. Clone and Install Dependencies

```bash
# Navigate to project directory
cd financial-insights-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

### 2. Setup Database

```bash
# Create database
sqlcmd -S localhost -U sa -P YourPassword -Q "CREATE DATABASE financial_insights_db"

# Run schema creation
sqlcmd -S localhost -U sa -P YourPassword -d financial_insights_db -i database/sample_schema/create_tables.sql

# Load sample data
sqlcmd -S localhost -U sa -P YourPassword -d financial_insights_db -i database/sample_schema/seed_data.sql
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required environment variables:
```env
# Azure AI Foundry
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string
AZURE_OPENAI_DEPLOYMENT_NAME=claude-3-5-sonnet

# MSSQL Database
MSSQL_SERVER=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=financial_insights_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPassword
```

### 4. Test MCP Server

```bash
# Run MCP server
cd mcp_servers/mssql_server
python server.py
```

Test with MCP client:
```bash
python mcp_servers/mcp_client.py
```

## Database Schema

### Tables

1. **portfolios**: Portfolio metadata
   - Columns: portfolio_id, name, strategy, risk_profile, inception_date, initial_capital, current_value

2. **holdings**: Current positions
   - Columns: holding_id, portfolio_id, symbol, asset_type, quantity, purchase_price, current_price

3. **transactions**: Historical trades
   - Columns: transaction_id, portfolio_id, symbol, transaction_type, quantity, price, transaction_date

4. **prices**: Daily market prices
   - Columns: price_id, symbol, price_date, open_price, high_price, low_price, close_price, volume

5. **benchmarks**: Index data (S&P 500, NASDAQ, Dow Jones)
   - Columns: benchmark_id, index_name, price_date, index_value, daily_return

### Views

- `vw_portfolio_performance`: Portfolio performance summary with returns
- `vw_holdings_with_prices`: Holdings with current prices and gains/losses
- `vw_sector_allocation`: Portfolio allocation by sector

### Stored Procedures

- `sp_calculate_portfolio_returns`: Calculate returns for date range
- `sp_update_holding_prices`: Update current prices from latest market data

## MCP Server Tools

The MSSQL MCP server provides 7 tools:

1. **execute_sql_query**: Execute SELECT queries (read-only for MVP)
2. **get_database_schema**: Get table schemas
3. **get_table_sample**: Get sample rows from tables
4. **validate_sql_query**: Validate SQL syntax
5. **get_table_names**: List all database tables
6. **test_connection**: Test database connectivity
7. **get_pool_status**: Get connection pool statistics

## Example Queries

Once agents are implemented, the system will handle queries like:

```
"What is my portfolio's total return over the last year?"
→ SQL Agent queries transactions and holdings
→ Data Analyst calculates returns
→ Domain Expert interprets performance

"Calculate the Sharpe ratio for my holdings vs S&P 500"
→ SQL Agent fetches portfolio and benchmark data
→ Data Analyst computes Sharpe ratio
→ Domain Expert provides risk-adjusted analysis

"Show me the top 5 performing stocks in my portfolio"
→ SQL Agent queries holdings with returns
→ Data Analyst ranks by performance
→ Domain Expert analyzes sector trends

"What is my portfolio's risk exposure by sector?"
→ SQL Agent gets sector allocation
→ Data Analyst calculates concentration metrics
→ Domain Expert assesses diversification
```

## Development Status

**Phase 1: Foundation** ✅ COMPLETED
- Project structure
- Configuration management
- Database schema
- Sample data

**Phase 2: MCP Server** ✅ COMPLETED
- Connection pooling
- 7 database tools
- MCP client

**Phase 3: Agents** 🚧 IN PROGRESS
- Base agent class
- SQL Agent
- Data Analyst Agent
- Domain Expert Agent

**Phase 4: Orchestration** 📋 PLANNED
- Hub coordinator
- Query router
- Agent handoffs

**Phase 5: API** 📋 PLANNED
- FastAPI endpoints
- WebSocket streaming
- Authentication

**Phase 6: Deployment** 📋 PLANNED
- Docker containerization
- Azure AI Foundry integration
- Infrastructure as Code

**Phase 7: Testing** 📋 PLANNED
- Unit tests
- Integration tests
- E2E tests

## Next Steps

1. Implement base agent class with Azure AI Foundry integration
2. Build SQL Agent with NL2SQL capabilities
3. Create Data Analyst Agent with code interpreter
4. Develop Domain Expert Agent with domain knowledge base
5. Implement orchestration hub
6. Build FastAPI REST API
7. Deploy to Azure AI Foundry

## Contributing

This is a production MVP implementation. Follow these guidelines:

- Use type hints for all functions
- Add docstrings for classes and methods
- Write unit tests for new features
- Follow existing code patterns
- Keep security in mind (SQL injection, input validation)

## License

MIT License

## Support

For issues and questions, please refer to the documentation or raise an issue in the repository.

---

**Status**: Active Development (MVP Phase)
**Last Updated**: 2025-12-10
**Version**: 0.1.0
