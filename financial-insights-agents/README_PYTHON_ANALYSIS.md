# Python Analysis Agent

> **Beyond t2sql**: Generate and execute complete Python analysis scripts from natural language queries.

## What is This?

The Python Analysis Agent is a revolutionary approach to data analysis that goes **far beyond traditional text-to-SQL (t2sql) agents**. Instead of just converting natural language to SQL queries, it:

1. **Generates complete Python scripts** for complex data analysis
2. **Executes them safely** in isolated Docker containers
3. **Returns structured results** with visualizations, metrics, and insights
4. **Handles advanced analytics**: statistics, ML, time series, optimization

## Why Not Just Use t2sql?

### t2sql Agents (Traditional):
```
User: "Analyze portfolio performance"
Agent: SELECT * FROM portfolio_returns
Result: Raw data table

→ You still need to:
  - Export the data
  - Write Python/R code
  - Calculate metrics
  - Create visualizations
  - Interpret results
```

### Python Analysis Agent (This System):
```
User: "Analyze portfolio performance with Sharpe ratio and charts"
Agent: [Generates & executes Python script]
Result:
  ✓ Sharpe Ratio: 1.85
  ✓ Max Drawdown: -12.3%
  ✓ Volatility: 15.2%
  ✓ Performance chart (PNG)
  ✓ Distribution plot (PNG)
  ✓ Natural language insights

→ Everything in one step!
```

## Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Code Generation** | Uses Claude to write Python scripts from natural language |
| 🔒 **Secure Sandbox** | Isolated Docker execution with resource limits |
| 📊 **Rich Outputs** | Visualizations, metrics, processed data, insights |
| 🛡️ **Safety First** | Code validation before execution |
| 📈 **Financial Focus** | Built-in templates for portfolio analysis |
| ⚡ **Batch Processing** | Run multiple analyses concurrently |
| 🎨 **Professional Viz** | Publication-quality plots with matplotlib/plotly |
| 🔬 **Full Data Science** | pandas, numpy, scipy, scikit-learn, statsmodels |

## Quick Start

### 1. Install

```bash
pip install -e .
cd tools/analytics/sandbox
docker build -t python-analysis-sandbox:latest .
export ANTHROPIC_API_KEY="your-key"
```

### 2. Run Your First Analysis

```python
import pandas as pd
from agents.python_analysis_agent import PythonAnalysisAgent

# Your data
df = pd.read_csv('portfolio.csv')

# Create agent
agent = PythonAnalysisAgent()

# Analyze
result = await agent.analyze(
    query="Calculate Sharpe ratio and create performance chart",
    data=df
)

# Results
print(result.insights)
print(f"Sharpe Ratio: {result.metrics['sharpe_ratio']}")
```

That's it! No manual coding required.

## What Can It Do?

### Financial Analysis
- Portfolio performance metrics (returns, Sharpe, Sortino, etc.)
- Risk analysis (VaR, CVaR, max drawdown)
- Attribution analysis
- Benchmark comparison
- Portfolio optimization

### Statistical Analysis
- Distribution testing
- Hypothesis testing
- Time series analysis
- Correlation analysis
- Regression models

### Machine Learning
- Predictive models
- Clustering
- Classification
- Feature importance
- Cross-validation

### Visualizations
- Time series plots
- Distribution histograms
- Correlation heatmaps
- Box plots
- Scatter plots
- Interactive Plotly charts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query (NL)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  1. Code Generator (Claude)                                 │
│     └─► Generates Python script from query + data context  │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  2. Safety Validator                                        │
│     └─► Checks for security risks, blocks dangerous code   │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  3. Docker Sandbox                                          │
│     • Isolated container (no network)                       │
│     • Resource limits (CPU, RAM, timeout)                   │
│     • Read-only filesystem                                  │
│     • Executes script with data                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  4. Result Processor                                        │
│     • Collects outputs (plots, metrics, data)              │
│     • Generates insights                                    │
│     • Formats for presentation                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  Structured Results                                         │
│  • Insights (text)                                          │
│  • Visualizations (PNG, HTML)                               │
│  • Metrics (JSON)                                           │
│  • Data outputs (CSV)                                       │
└─────────────────────────────────────────────────────────────┘
```

## Documentation

- **[Full Documentation](docs/PYTHON_ANALYSIS_AGENT.md)** - Complete guide
- **[Quick Start](docs/QUICKSTART_PYTHON_ANALYSIS.md)** - Get started in 5 minutes
- **[Examples](examples/python_analysis_demo.py)** - Demo scripts

## Comparison: t2sql vs Python Analysis Agent

| Capability | t2sql Agent | Python Analysis Agent |
|------------|-------------|----------------------|
| Generate SQL | ✅ | ✅ (via SQL agent integration) |
| Execute SQL | ✅ | ✅ (via SQL agent) |
| Generate Python | ❌ | ✅ |
| Execute Python | ❌ | ✅ |
| Statistical tests | ❌ | ✅ (scipy, statsmodels) |
| Machine learning | ❌ | ✅ (scikit-learn) |
| Visualizations | ❌ | ✅ (matplotlib, plotly, seaborn) |
| Natural language insights | ❌ | ✅ |
| Advanced analytics | ❌ | ✅ |
| Batch processing | Partial | ✅ |
| Safety validation | N/A | ✅ |
| Sandboxed execution | N/A | ✅ |

## Use Cases

### 1. Financial Portfolio Analysis
```python
result = await agent.analyze(
    "Calculate portfolio metrics and compare to S&P 500",
    portfolio_df
)
```

### 2. Risk Assessment
```python
result = await agent.analyze(
    "Calculate VaR and CVaR at 95% confidence level",
    returns_df
)
```

### 3. Predictive Modeling
```python
result = await agent.analyze(
    "Build a linear regression model to predict returns",
    features_df
)
```

### 4. Time Series Analysis
```python
result = await agent.analyze(
    "Perform time series decomposition and test for stationarity",
    timeseries_df
)
```

## Security & Safety

✅ **Code Validation**: All scripts validated before execution
✅ **Sandboxed**: Complete isolation via Docker
✅ **No Network**: Container has no network access
✅ **Resource Limits**: CPU, memory, and time constraints
✅ **Read-Only**: Filesystem is read-only except output dirs
✅ **Non-Root**: Code runs as unprivileged user

## Performance

- **Typical execution**: 10-30 seconds
- **Complex analyses**: 30-120 seconds
- **Concurrent analyses**: Up to N simultaneous (configurable)
- **Resource limits**: 2 CPU cores, 2GB RAM per container

## Integration

### With SQL Agent
```python
# 1. Get data via SQL
data = await sql_agent.query("SELECT * FROM portfolio")

# 2. Analyze with Python
result = await python_agent.analyze(
    "Calculate risk metrics",
    data
)
```

### In FastAPI
```python
@app.post("/analyze")
async def analyze(query: str, data_id: str):
    data = get_data(data_id)
    result = await python_agent.analyze(query, data)
    return result
```

## Examples

Run the demo:

```bash
cd examples
python python_analysis_demo.py
```

This runs 4 demos:
1. Portfolio performance analysis
2. Correlation analysis
3. Distribution analysis
4. Batch processing

## Requirements

- Python 3.11+
- Docker
- Anthropic API key
- 4GB+ RAM recommended

## Contributing

Contributions welcome! Areas for enhancement:
- Additional code templates
- More visualization types
- ML model templates
- Performance optimizations

## License

See main project LICENSE.

## Support

- **Issues**: GitHub Issues
- **Docs**: `/docs/`
- **Examples**: `/examples/`

---

**Built for serious financial analysis.** 🚀

Beyond SQL queries. Beyond simple charts. **Complete analysis automation.**
