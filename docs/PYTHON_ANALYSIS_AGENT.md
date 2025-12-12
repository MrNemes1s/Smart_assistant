# Python Analysis Agent

## Overview

The **Python Analysis Agent** is a dynamic script generation and execution system that goes beyond traditional text-to-SQL (t2sql) agents. Instead of just converting natural language to SQL queries, it generates complete Python analysis scripts and executes them safely in isolated Docker containers.

## Key Differences from t2sql Agents

| Feature | t2sql Agents | Python Analysis Agent |
|---------|--------------|----------------------|
| **Output** | SQL queries only | Complete Python scripts |
| **Capabilities** | Database queries | Complex analysis, ML, statistics, visualizations |
| **Execution** | Database engine | Isolated Docker sandbox |
| **Results** | Query results (tables) | Insights, plots, metrics, processed data |
| **Analysis Depth** | Limited to SQL operations | Full data science stack |
| **Visualizations** | None (requires separate step) | Generated automatically |
| **Statistical Tests** | Basic aggregations only | scipy, statsmodels, scikit-learn |
| **Machine Learning** | Not supported | Full ML capabilities |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Python Analysis Agent                       │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─► 1. Code Generator (Claude)
             │     └─► Generates Python scripts from NL queries
             │
             ├─► 2. Safety Validator
             │     └─► Validates code for security risks
             │
             ├─► 3. Sandbox Executor (Docker)
             │     └─► Executes code in isolated container
             │
             └─► 4. Result Processor
                   └─► Formats outputs (plots, metrics, insights)
```

## Components

### 1. Code Generator (`code_generator.py`)

Uses Claude to generate Python analysis scripts based on:
- User's natural language query
- Data context (columns, types, sample data)
- Analysis type hint (optional)

**Example Input:**
```
Query: "Analyze portfolio returns and calculate Sharpe ratio. Create visualization."
Data: DataFrame with columns [date, portfolio_value, sp500_value]
```

**Example Output:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

# Load data
with open('/sandbox/data/data.pkl', 'rb') as f:
    df = pickle.load(f)

# Calculate returns
df['returns'] = df['portfolio_value'].pct_change()

# Calculate Sharpe ratio
sharpe = df['returns'].mean() / df['returns'].std() * np.sqrt(252)

# Save metrics
metrics = {'sharpe_ratio': float(sharpe)}
with open('/sandbox/outputs/metrics.json', 'w') as f:
    json.dump(metrics, f)

# Create plot
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['portfolio_value'])
plt.title('Portfolio Performance')
plt.savefig('/sandbox/outputs/plot_performance.png')
```

### 2. Safety Validator (`safety_validator.py`)

Validates generated code for security risks before execution:

**Blocked Operations:**
- Dangerous imports (`os`, `subprocess`, `socket`, etc.)
- Code execution functions (`eval`, `exec`, `compile`)
- System commands
- Network operations
- File access outside `/sandbox/data` and `/sandbox/outputs`

**Risk Levels:**
- `safe`: No violations or warnings
- `low`: Minor warnings only
- `medium`: Multiple warnings
- `high`: Violations detected
- `critical`: Severe security risks

### 3. Sandbox Executor (`sandbox/executor.py`)

Executes scripts in isolated Docker containers with:

**Security Features:**
- Read-only filesystem (except output directories)
- No network access (`network_mode: none`)
- Non-root user execution
- Resource limits (2 CPU cores, 2GB RAM)
- Execution timeout (default 5 minutes)

**Data Exchange:**
- Input: Data pickled to `/sandbox/data/data.pkl`
- Output: Results written to `/sandbox/outputs/`

### 4. Result Processor (`result_processor.py`)

Processes execution outputs into structured format:

**Output Types:**
- **Visualizations**: PNG images, HTML plots (Plotly)
- **Metrics**: JSON with calculated statistics
- **Insights**: Natural language summary
- **Data**: Processed CSV/text files

## Usage

### Basic Usage

```python
import pandas as pd
from agents.python_analysis_agent import PythonAnalysisAgent

# Initialize agent
agent = PythonAnalysisAgent(
    anthropic_api_key="your-api-key",
    build_sandbox=True  # First time only
)

# Load your data
df = pd.read_csv('portfolio.csv')

# Run analysis
result = await agent.analyze(
    query="Calculate monthly returns and create a time series plot",
    data=df,
    analysis_type="visualization"
)

# Access results
print(result.insights)
print(f"Metrics: {result.metrics}")
print(f"Generated {len(result.visualizations)} plots")

# Cleanup
agent.cleanup()
```

### Quick Analysis (Convenience Function)

```python
from agents.python_analysis_agent import quick_analyze

result = await quick_analyze(
    query="Show correlation between portfolio and S&P 500",
    data=df,
    anthropic_api_key="your-api-key"
)

print(result.insights)
```

### Batch Analysis

```python
queries = [
    "Calculate Sharpe ratio and volatility",
    "Create returns distribution histogram",
    "Analyze correlation with benchmark"
]

results = await agent.batch_analyze(queries, df, max_concurrent=2)

for result in results:
    print(f"Query: {result.query}")
    print(f"Success: {result.success}")
    print(f"Insights: {result.insights}\n")
```

## Example Queries

### Financial Analysis

1. **Performance Metrics**
   ```
   "Calculate total returns, Sharpe ratio, max drawdown, and volatility.
    Create a performance chart with drawdown overlay."
   ```

2. **Correlation Analysis**
   ```
   "Analyze correlation between all holdings. Create a heatmap and
    identify the strongest correlations."
   ```

3. **Risk Analysis**
   ```
   "Calculate Value at Risk (95% confidence) and Conditional VaR.
    Show distribution of returns with VaR markers."
   ```

4. **Portfolio Optimization**
   ```
   "Calculate optimal portfolio weights using mean-variance optimization.
    Plot efficient frontier and current portfolio position."
   ```

### Statistical Analysis

5. **Time Series Analysis**
   ```
   "Perform time series decomposition (trend, seasonal, residual).
    Test for stationarity using ADF test."
   ```

6. **Hypothesis Testing**
   ```
   "Test if portfolio returns are significantly different from zero.
    Perform t-test and show confidence intervals."
   ```

### Machine Learning

7. **Prediction**
   ```
   "Build a linear regression model to predict returns based on
    market indicators. Show feature importance."
   ```

8. **Clustering**
   ```
   "Cluster stocks based on return patterns using K-means.
    Visualize clusters and show characteristics."
   ```

## Code Templates

Pre-built templates for common analyses:

```python
from agents.data_analyst_agent.code_templates.financial_templates import (
    get_template,
    list_templates
)

# List available templates
templates = list_templates()
# ['portfolio_performance', 'correlation', 'distribution', 'time_series']

# Get template code
template_code = get_template('portfolio_performance')
```

## Configuration

### Environment Variables

```bash
# Anthropic API
ANTHROPIC_API_KEY=your-api-key

# Docker Settings (optional)
DOCKER_IMAGE_NAME=python-analysis-sandbox:latest
SANDBOX_TIMEOUT=300
SANDBOX_MEMORY_LIMIT=2g
SANDBOX_CPU_LIMIT=2.0
```

### Docker Setup

Build the sandbox image:

```bash
cd financial-insights-agents/tools/analytics/sandbox
docker build -t python-analysis-sandbox:latest .
```

Or use docker-compose:

```bash
docker-compose build
```

## Safety & Security

### Built-in Protections

1. **Code Validation**: All code validated before execution
2. **Sandboxing**: Complete isolation via Docker
3. **Resource Limits**: CPU, memory, and time constraints
4. **No Network**: Container has no network access
5. **Restricted Filesystem**: Read-only except output directories
6. **Non-root User**: Code runs as unprivileged user

### Best Practices

1. Always review generated code in logs (debug mode)
2. Monitor resource usage for long-running analyses
3. Set appropriate timeouts for complex operations
4. Regularly update the Docker image with security patches
5. Use separate API keys for production vs development

## Integration with Data Pipeline

### With SQL Agent

```python
from agents.sql_agent import SQLAgent
from agents.python_analysis_agent import PythonAnalysisAgent

# 1. SQL Agent fetches data
sql_agent = SQLAgent()
data = await sql_agent.query("SELECT * FROM portfolio_holdings")

# 2. Python Agent analyzes
python_agent = PythonAnalysisAgent()
result = await python_agent.analyze(
    query="Calculate portfolio metrics and create visualizations",
    data=data
)
```

### In Backend API

```python
from fastapi import FastAPI, HTTPException
from agents.python_analysis_agent import PythonAnalysisAgent
import pandas as pd

app = FastAPI()
agent = PythonAnalysisAgent()

@app.post("/analyze")
async def analyze(query: str, session_id: str):
    # Get data from session
    data = get_session_data(session_id)

    # Run analysis
    result = await agent.analyze(query, data)

    if not result.success:
        raise HTTPException(500, detail=result.error)

    return {
        "insights": result.insights,
        "metrics": result.metrics,
        "visualizations": [
            {
                "title": viz["title"],
                "data": viz["data"],
                "type": viz["format"]
            }
            for viz in result.visualizations
        ]
    }
```

## Troubleshooting

### Docker Issues

**Problem**: "Docker image not found"
```bash
# Build the image
cd tools/analytics/sandbox
docker build -t python-analysis-sandbox:latest .
```

**Problem**: "Permission denied" when executing
```bash
# Check Docker daemon is running
docker ps

# Ensure user is in docker group (Linux)
sudo usermod -aG docker $USER
```

### Execution Errors

**Problem**: Code validation fails
- Review validation violations in logs
- Check for disallowed imports or functions
- Ensure code only accesses allowed paths

**Problem**: Timeout errors
- Increase timeout parameter: `agent.analyze(..., timeout=600)`
- Simplify analysis query
- Optimize data size before analysis

### Memory Issues

**Problem**: Container killed due to memory
- Reduce data size before analysis
- Increase memory limit in docker-compose.yml
- Use sampling for large datasets

## Performance Tips

1. **Data Sampling**: For exploratory analysis, sample large datasets
2. **Batch Operations**: Use `batch_analyze()` for multiple queries
3. **Caching**: Cache analysis results for repeat queries
4. **Timeout Tuning**: Set appropriate timeouts based on complexity
5. **Resource Monitoring**: Monitor Docker resource usage

## API Reference

### PythonAnalysisAgent

```python
class PythonAnalysisAgent:
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        build_sandbox: bool = False
    )

    async def analyze(
        self,
        query: str,
        data: pd.DataFrame,
        analysis_type: Optional[str] = None,
        timeout: int = 300
    ) -> AnalysisResult

    async def batch_analyze(
        self,
        queries: List[str],
        data: pd.DataFrame,
        max_concurrent: int = 3
    ) -> List[AnalysisResult]

    def cleanup(self) -> None
```

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    success: bool
    query: str
    insights: str
    visualizations: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    data_outputs: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None
    raw_output: Optional[str] = None
```

## Future Enhancements

- [ ] Support for streaming execution logs
- [ ] Integration with MLflow for experiment tracking
- [ ] Persistent cache for common analyses
- [ ] Support for custom library installations
- [ ] Interactive Jupyter-style notebooks
- [ ] GPU support for ML models
- [ ] Multi-language support (R, Julia)
- [ ] Collaborative analysis sessions

## Contributing

When adding new features:

1. Add comprehensive tests
2. Update safety validator for new risks
3. Document new capabilities
4. Add example queries
5. Update code templates if applicable

## License

See main project LICENSE file.

## Support

For issues or questions:
- GitHub Issues: [project-repo]/issues
- Documentation: [project-repo]/docs
- Examples: `/docs/examples/python_analysis_examples.ipynb`
