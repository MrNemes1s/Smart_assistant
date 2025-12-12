"""
Python Analysis Agent Demo
Demonstrates the capabilities of the Python Analysis Agent
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from agents.python_analysis_agent import PythonAnalysisAgent


def create_sample_portfolio_data() -> pd.DataFrame:
    """Create sample portfolio data for testing"""
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=252, freq='D')

    # Simulate portfolio and benchmark returns
    portfolio_returns = np.random.normal(0.0008, 0.015, 252)
    benchmark_returns = np.random.normal(0.0005, 0.012, 252)

    # Calculate cumulative values
    portfolio_value = 100000 * (1 + portfolio_returns).cumprod()
    benchmark_value = 100000 * (1 + benchmark_returns).cumprod()

    return pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_value,
        'benchmark_value': benchmark_value,
        'cash_position': np.linspace(10000, 5000, 252),
        'total_invested': portfolio_value + np.linspace(10000, 5000, 252)
    })


async def demo_portfolio_performance():
    """Demo: Portfolio performance analysis"""
    print("\n" + "="*70)
    print("DEMO 1: Portfolio Performance Analysis")
    print("="*70)

    data = create_sample_portfolio_data()

    agent = PythonAnalysisAgent()

    result = await agent.analyze(
        query="""Analyze portfolio performance:
        1. Calculate total return, annualized return, and volatility
        2. Calculate Sharpe ratio (assume risk-free rate of 2%)
        3. Calculate maximum drawdown
        4. Compare performance vs benchmark
        5. Create a line chart showing portfolio vs benchmark over time
        6. Save all metrics to JSON
        """,
        data=data,
        analysis_type="visualization",
        timeout=180
    )

    print(f"\n✓ Analysis completed in {result.execution_time:.2f}s")
    print(f"✓ Success: {result.success}")

    if result.success:
        print("\n" + "-"*70)
        print("INSIGHTS:")
        print("-"*70)
        print(result.insights)

        print("\n" + "-"*70)
        print("METRICS:")
        print("-"*70)
        for key, value in result.metrics.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")

        print("\n" + "-"*70)
        print("VISUALIZATIONS:")
        print("-"*70)
        for i, viz in enumerate(result.visualizations, 1):
            print(f"{i}. {viz['title']} ({viz['format'].upper()})")
    else:
        print(f"\n✗ Error: {result.error}")
        print(f"Output: {result.raw_output}")

    agent.cleanup()


async def demo_correlation_analysis():
    """Demo: Correlation analysis"""
    print("\n" + "="*70)
    print("DEMO 2: Correlation Analysis")
    print("="*70)

    # Create multi-asset data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=252)

    # Create correlated returns
    base = np.random.randn(252)
    data = pd.DataFrame({
        'date': dates,
        'us_stocks': base + np.random.randn(252) * 0.5,
        'international_stocks': base * 0.7 + np.random.randn(252) * 0.6,
        'bonds': -base * 0.3 + np.random.randn(252) * 0.4,
        'real_estate': base * 0.5 + np.random.randn(252) * 0.5,
        'commodities': np.random.randn(252) * 0.8
    })

    agent = PythonAnalysisAgent()

    result = await agent.analyze(
        query="""Analyze correlations between asset classes:
        1. Calculate correlation matrix
        2. Create a correlation heatmap
        3. Identify the strongest positive correlation
        4. Identify the strongest negative correlation
        5. Provide insights about diversification
        """,
        data=data,
        timeout=180
    )

    print(f"\n✓ Analysis completed in {result.execution_time:.2f}s")

    if result.success:
        print("\n" + "-"*70)
        print("INSIGHTS:")
        print("-"*70)
        print(result.insights)

        print("\n" + "-"*70)
        print("VISUALIZATIONS:")
        print("-"*70)
        for viz in result.visualizations:
            print(f"- {viz['title']}")
    else:
        print(f"\n✗ Error: {result.error}")

    agent.cleanup()


async def demo_distribution_analysis():
    """Demo: Distribution and statistical analysis"""
    print("\n" + "="*70)
    print("DEMO 3: Distribution Analysis")
    print("="*70)

    # Create returns data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=252)

    # Slightly skewed returns (more common in financial data)
    returns = np.random.gamma(2, 0.005, 252) - 0.008

    data = pd.DataFrame({
        'date': dates,
        'daily_returns': returns
    })

    agent = PythonAnalysisAgent()

    result = await agent.analyze(
        query="""Analyze return distribution:
        1. Test for normality (Shapiro-Wilk or similar)
        2. Calculate skewness and kurtosis
        3. Calculate percentiles (5th, 25th, 50th, 75th, 95th)
        4. Create histogram with normal distribution overlay
        5. Create Q-Q plot
        6. Provide interpretation of the results
        """,
        data=data,
        analysis_type="statistics",
        timeout=180
    )

    print(f"\n✓ Analysis completed in {result.execution_time:.2f}s")

    if result.success:
        print("\n" + "-"*70)
        print("INSIGHTS:")
        print("-"*70)
        print(result.insights)

        print("\n" + "-"*70)
        print("KEY STATISTICS:")
        print("-"*70)
        for key, value in result.metrics.items():
            print(f"{key}: {value}")
    else:
        print(f"\n✗ Error: {result.error}")

    agent.cleanup()


async def demo_batch_analysis():
    """Demo: Batch analysis"""
    print("\n" + "="*70)
    print("DEMO 4: Batch Analysis (Multiple Queries)")
    print("="*70)

    data = create_sample_portfolio_data()

    queries = [
        "Calculate basic performance metrics: total return, volatility, Sharpe ratio",
        "Analyze the distribution of daily returns",
        "Calculate rolling 30-day volatility and plot it"
    ]

    agent = PythonAnalysisAgent()

    print(f"\nRunning {len(queries)} analyses...")

    results = await agent.batch_analyze(queries, data, max_concurrent=2)

    for i, result in enumerate(results, 1):
        print(f"\n{'-'*70}")
        print(f"QUERY {i}: {result.query[:60]}...")
        print(f"{'-'*70}")
        print(f"Success: {result.success}")
        print(f"Time: {result.execution_time:.2f}s")

        if result.success:
            print(f"\nInsights:\n{result.insights[:200]}...")
            print(f"\nMetrics: {len(result.metrics)} metrics")
            print(f"Visualizations: {len(result.visualizations)} plots")
        else:
            print(f"Error: {result.error}")

    agent.cleanup()


async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("Python Analysis Agent - Demonstration")
    print("="*70)
    print("\nThis demo showcases the Python Analysis Agent's capabilities")
    print("to generate and execute data analysis scripts in a sandbox.\n")

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key'\n")
        return

    try:
        # Run demos
        await demo_portfolio_performance()
        await asyncio.sleep(2)

        await demo_correlation_analysis()
        await asyncio.sleep(2)

        await demo_distribution_analysis()
        await asyncio.sleep(2)

        await demo_batch_analysis()

        print("\n" + "="*70)
        print("All demos completed!")
        print("="*70)
        print("\nKey Takeaways:")
        print("• Generated complete Python scripts from natural language")
        print("• Executed safely in isolated Docker containers")
        print("• Produced visualizations, metrics, and insights automatically")
        print("• Handled multiple analysis types: performance, statistics, ML")
        print("\nThis is fundamentally different from t2sql agents that only")
        print("generate SQL queries. This system generates complete analysis")
        print("pipelines with visualizations and insights!")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
