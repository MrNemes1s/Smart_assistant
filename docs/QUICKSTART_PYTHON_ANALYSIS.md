# Quick Start: Python Analysis Agent

Get started with the Python Analysis Agent in 5 minutes!

## Prerequisites

- Python 3.11+
- Docker installed and running
- Anthropic API key

## Installation

### 1. Install Dependencies

```bash
cd financial-insights-agents
pip install -e .
```

### 2. Build Docker Sandbox

```bash
cd tools/analytics/sandbox
docker build -t python-analysis-sandbox:latest .
```

Or use docker-compose:

```bash
docker-compose build
```

### 3. Set Environment Variables

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## First Analysis

### Example 1: Portfolio Performance

```python
import asyncio
import pandas as pd
from agents.python_analysis_agent import PythonAnalysisAgent

async def main():
    # Create sample portfolio data
    data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'portfolio_value': [10000 * (1 + i * 0.01 + np.random.normal(0, 0.005))
                           for i in range(100)],
        'benchmark_value': [10000 * (1 + i * 0.008 + np.random.normal(0, 0.004))
                          for i in range(100)]
    })

    # Initialize agent
    agent = PythonAnalysisAgent()

    # Run analysis
    result = await agent.analyze(
        query="""Calculate portfolio performance metrics:
        - Total return
        - Annualized return
        - Volatility
        - Sharpe ratio
        - Max drawdown

        Create a time series plot comparing portfolio vs benchmark.
        """,
        data=data
    )

    # Print results
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    print(result.insights)
    print("\nMetrics:")
    for key, value in result.metrics.items():
        print(f"  {key}: {value}")

    print(f"\nVisualizations: {len(result.visualizations)}")
    for viz in result.visualizations:
        print(f"  - {viz['title']}")

    print(f"\nExecution time: {result.execution_time:.2f}s")

    # Cleanup
    agent.cleanup()

if __name__ == "__main__":
    import numpy as np
    asyncio.run(main())
```

### Example 2: Statistical Analysis

```python
async def statistical_analysis():
    # Sample returns data
    data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=252),
        'daily_returns': np.random.normal(0.001, 0.02, 252)
    })

    agent = PythonAnalysisAgent()

    result = await agent.analyze(
        query="""Analyze the distribution of returns:
        - Test for normality
        - Calculate skewness and kurtosis
        - Create histogram with normal distribution overlay
        - Create Q-Q plot
        """,
        data=data,
        analysis_type="statistics"
    )

    print(result.insights)
    agent.cleanup()

asyncio.run(statistical_analysis())
```

### Example 3: Correlation Analysis

```python
async def correlation_analysis():
    # Multi-asset portfolio
    data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'tech_stocks': np.random.randn(100).cumsum(),
        'energy_stocks': np.random.randn(100).cumsum(),
        'financial_stocks': np.random.randn(100).cumsum(),
        'real_estate': np.random.randn(100).cumsum()
    })

    agent = PythonAnalysisAgent()

    result = await agent.analyze(
        query="""Analyze correlations between sectors:
        - Calculate correlation matrix
        - Create heatmap
        - Identify strongest positive and negative correlations
        """,
        data=data
    )

    print(result.insights)
    print("\nCorrelation Matrix:")
    print(result.metrics.get('correlation_matrix', {}))

    agent.cleanup()

asyncio.run(correlation_analysis())
```

## What Makes This Different?

### Traditional t2sql Agent:

```
User: "Show me portfolio returns"
Agent: SELECT portfolio_id, returns FROM portfolio_performance
Result: Table with raw data
```

You still need to:
- Export data
- Write Python/R code
- Create visualizations
- Calculate statistics
- Interpret results

### Python Analysis Agent:

```
User: "Analyze portfolio returns with visualizations and insights"
Agent: [Generates complete Python script]
Result:
  - Line chart of returns over time
  - Distribution histogram
  - Sharpe ratio: 1.8
  - Max drawdown: -15.2%
  - Natural language insights about performance
```

Everything in one step!

## Common Use Cases

### 1. Quick Data Exploration

```python
result = await agent.analyze(
    query="Give me an overview of this data with summary statistics and distributions",
    data=df
)
```

### 2. Financial Metrics

```python
result = await agent.analyze(
    query="Calculate all standard portfolio risk metrics",
    data=portfolio_df
)
```

### 3. Comparative Analysis

```python
result = await agent.analyze(
    query="Compare performance across all holdings, show top and bottom performers",
    data=holdings_df
)
```

### 4. Trend Analysis

```python
result = await agent.analyze(
    query="Identify trends and patterns in the time series data",
    data=timeseries_df
)
```

### 5. Custom ML Models

```python
result = await agent.analyze(
    query="Build a predictive model for returns using available features",
    data=features_df
)
```

## Integration with Your App

### Option 1: Direct Integration

```python
from agents.python_analysis_agent import PythonAnalysisAgent

app_agent = PythonAnalysisAgent()

# In your API endpoint
@app.post("/analyze")
async def analyze_endpoint(query: str, data_id: str):
    data = load_data(data_id)
    result = await app_agent.analyze(query, data)
    return result
```

### Option 2: With SQL Agent Pipeline

```python
# Step 1: SQL Agent gets data
sql_result = await sql_agent.execute(
    "Get portfolio holdings with prices"
)

# Step 2: Python Agent analyzes
analysis_result = await python_agent.analyze(
    query="Analyze portfolio allocation and performance",
    data=sql_result.data
)
```

## Tips for Best Results

### 1. Be Specific

❌ "Analyze this data"
✅ "Calculate correlation between all numeric columns and create a heatmap"

### 2. Combine Multiple Tasks

✅ "Calculate Sharpe ratio, create a returns chart, and identify the worst drawdown period"

### 3. Request Specific Visualizations

✅ "Create three plots: 1) time series, 2) distribution histogram, 3) correlation heatmap"

### 4. Ask for Comparisons

✅ "Compare portfolio performance against S&P 500 benchmark"

### 5. Request Insights

✅ "Calculate metrics and provide insights about what they mean for portfolio health"

## Next Steps

1. **Read Full Documentation**: See `PYTHON_ANALYSIS_AGENT.md`
2. **Explore Templates**: Check `agents/data_analyst_agent/code_templates/`
3. **View Examples**: Run example scripts in `/examples/`
4. **Customize**: Modify code generator prompts for your domain
5. **Integrate**: Add to your application workflow

## Troubleshooting

### "Docker image not found"

```bash
cd tools/analytics/sandbox
docker build -t python-analysis-sandbox:latest .
```

### "Permission denied"

```bash
# Ensure Docker daemon is running
docker ps

# Add user to docker group (Linux/Mac)
sudo usermod -aG docker $USER
```

### "Timeout error"

```python
# Increase timeout
result = await agent.analyze(query, data, timeout=600)
```

### "API key error"

```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-key"

# Or pass directly
agent = PythonAnalysisAgent(anthropic_api_key="your-key")
```

## Support

- **Documentation**: `/docs/PYTHON_ANALYSIS_AGENT.md`
- **Examples**: `/examples/python_analysis_examples.py`
- **Issues**: GitHub Issues

## What's Next?

Try more advanced features:
- Batch analysis
- Custom templates
- ML model training
- Real-time streaming analysis

Happy analyzing! 🚀
