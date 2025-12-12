"""
Python Analysis Agent - Dynamic Script Generation & Execution
Different from t2sql: Generates and executes Python code for complex analysis,
not just SQL queries. Handles visualizations, statistics, ML, and insights.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from tools.analytics.code_generator import CodeGenerator
from tools.analytics.sandbox.executor import SandboxExecutor, ExecutionResult
from tools.analytics.result_processor import ResultProcessor, AnalysisResult
from tools.analytics.safety_validator import SafetyValidator

logger = logging.getLogger(__name__)


class PythonAnalysisAgent:
    """
    Agent that generates and executes Python analysis scripts in sandbox

    Key Differences from t2sql agents:
    1. Generates Python code, not SQL queries
    2. Performs complex analysis beyond database queries
    3. Creates visualizations (matplotlib, plotly, seaborn)
    4. Runs statistical tests and ML models
    5. Executes in isolated Docker sandbox
    6. Returns insights, plots, and metrics
    """

    def __init__(self,
                 anthropic_api_key: Optional[str] = None,
                 model: str = "claude-3-5-sonnet-20241022",
                 build_sandbox: bool = False):
        """
        Initialize Python Analysis Agent

        Args:
            anthropic_api_key: API key for Claude
            model: Claude model to use
            build_sandbox: Whether to build Docker image on init
        """
        self.code_generator = CodeGenerator(api_key=anthropic_api_key, model=model)
        self.sandbox_executor = SandboxExecutor(build_image=build_sandbox)
        self.result_processor = ResultProcessor()
        self.safety_validator = SafetyValidator(strict_mode=True)

        logger.info("Python Analysis Agent initialized")

    async def analyze(self,
                     query: str,
                     data: pd.DataFrame,
                     analysis_type: Optional[str] = None,
                     timeout: int = 300) -> AnalysisResult:
        """
        Perform analysis on data based on natural language query

        Args:
            query: User's natural language analysis request
            data: Pandas DataFrame to analyze
            analysis_type: Optional hint (visualization, statistics, ml, etc.)
            timeout: Max execution time in seconds

        Returns:
            AnalysisResult with insights, visualizations, and metrics

        Example:
            >>> agent = PythonAnalysisAgent()
            >>> df = pd.read_csv('portfolio.csv')
            >>> result = await agent.analyze(
            ...     "Create a time series plot of portfolio returns and calculate Sharpe ratio",
            ...     data=df
            ... )
            >>> print(result.insights)
            >>> for viz in result.visualizations:
            ...     print(f"Generated: {viz['title']}")
        """
        logger.info(f"Starting analysis: {query[:100]}...")

        try:
            # Step 1: Prepare data context for code generation
            data_context = self._prepare_data_context(data)

            # Step 2: Generate Python analysis code
            logger.info("Generating analysis code...")
            code = await self.code_generator.generate(
                query=query,
                data_context=data_context,
                analysis_type=analysis_type
            )

            logger.debug(f"Generated code:\n{code[:500]}...")

            # Step 2.5: Validate code safety
            logger.info("Validating code safety...")
            validation_result = self.safety_validator.validate(code)

            if not validation_result.is_safe:
                logger.error(f"Code validation failed: {validation_result.violations}")
                return AnalysisResult(
                    success=False,
                    query=query,
                    insights=f"Code validation failed. Security violations detected:\n" +
                            "\n".join(f"• {v}" for v in validation_result.violations),
                    visualizations=[],
                    metrics={},
                    data_outputs={},
                    execution_time=0.0,
                    error="Code safety validation failed"
                )

            if validation_result.warnings:
                logger.warning(f"Code validation warnings: {validation_result.warnings}")

            # Step 3: Execute in sandbox
            logger.info("Executing code in sandbox...")
            execution_result = await self.sandbox_executor.execute(
                script=code,
                data={'data': data},  # Will be saved as data.pkl
                timeout=timeout
            )

            logger.info(f"Execution completed: success={execution_result.success}, "
                       f"time={execution_result.execution_time:.2f}s")

            # Step 4: Generate insights if execution succeeded
            insights = None
            if execution_result.success:
                logger.info("Generating insights...")
                insights = await self.code_generator.generate_insights(
                    query=query,
                    outputs=execution_result.outputs,
                    execution_result=execution_result
                )

            # Step 5: Process results
            result = self.result_processor.process(
                query=query,
                execution_result=execution_result,
                insights=insights
            )

            return result

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return AnalysisResult(
                success=False,
                query=query,
                insights=f"Analysis failed with error: {str(e)}",
                visualizations=[],
                metrics={},
                data_outputs={},
                execution_time=0.0,
                error=str(e)
            )

    def _prepare_data_context(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Prepare data context for code generation

        Args:
            data: Pandas DataFrame

        Returns:
            Dictionary with data metadata
        """
        context = {
            'columns': data.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'shape': data.shape,
            'sample': data.head(5).to_string() if len(data) > 0 else "Empty DataFrame"
        }

        # Add statistics for numeric columns
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            context['numeric_columns'] = numeric_cols
            context['statistics'] = data[numeric_cols].describe().to_dict()

        # Add date columns if any
        date_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols:
            context['date_columns'] = date_cols

        return context

    async def batch_analyze(self,
                          queries: List[str],
                          data: pd.DataFrame,
                          max_concurrent: int = 3) -> List[AnalysisResult]:
        """
        Perform multiple analyses concurrently

        Args:
            queries: List of analysis queries
            data: DataFrame to analyze
            max_concurrent: Max concurrent executions

        Returns:
            List of AnalysisResults
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_with_semaphore(query: str) -> AnalysisResult:
            async with semaphore:
                return await self.analyze(query, data)

        tasks = [analyze_with_semaphore(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(AnalysisResult(
                    success=False,
                    query=queries[i],
                    insights=f"Error: {str(result)}",
                    visualizations=[],
                    metrics={},
                    data_outputs={},
                    execution_time=0.0,
                    error=str(result)
                ))
            else:
                final_results.append(result)

        return final_results

    def cleanup(self):
        """Cleanup resources (containers, etc.)"""
        logger.info("Cleaning up resources...")
        self.sandbox_executor.cleanup_all()


# Convenience function for quick analysis
async def quick_analyze(
    query: str,
    data: pd.DataFrame,
    anthropic_api_key: Optional[str] = None
) -> AnalysisResult:
    """
    Quick analysis without creating agent instance

    Args:
        query: Analysis query
        data: Data to analyze
        anthropic_api_key: API key

    Returns:
        AnalysisResult
    """
    agent = PythonAnalysisAgent(anthropic_api_key=anthropic_api_key)
    try:
        return await agent.analyze(query, data)
    finally:
        agent.cleanup()


# Example usage
if __name__ == "__main__":
    import os
    from pathlib import Path

    async def main():
        # Example: Analyze financial portfolio data
        api_key = os.getenv("ANTHROPIC_API_KEY")

        # Create sample data
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'portfolio_value': [10000 * (1 + i * 0.01) for i in range(100)],
            'sp500_value': [4500 * (1 + i * 0.008) for i in range(100)],
            'cash': [5000 - i * 10 for i in range(100)]
        })

        agent = PythonAnalysisAgent(anthropic_api_key=api_key, build_sandbox=True)

        try:
            # Run analysis
            result = await agent.analyze(
                query="Create a line plot comparing portfolio value vs S&P 500. Calculate the correlation and beta. Provide insights on performance.",
                data=data,
                analysis_type="visualization"
            )

            # Display results
            print("\n" + "="*60)
            print("ANALYSIS RESULTS")
            print("="*60)
            print(result.insights)
            print("\nMetrics:", result.metrics)
            print(f"\nVisualizations: {len(result.visualizations)}")
            print(f"Execution time: {result.execution_time:.2f}s")

        finally:
            agent.cleanup()

    asyncio.run(main())
