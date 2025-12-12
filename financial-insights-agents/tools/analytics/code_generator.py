"""
Python Code Generator for Data Analysis
Uses Claude to generate analysis scripts based on user queries and data context
"""
import logging
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

logger = logging.getLogger(__name__)


class CodeGenerator:
    """Generates Python analysis code using Claude"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize code generator

        Args:
            api_key: Anthropic API key (optional, reads from env if not provided)
            model: Claude model to use
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

    async def generate(self,
                      query: str,
                      data_context: Dict[str, Any],
                      analysis_type: Optional[str] = None) -> str:
        """
        Generate Python analysis code

        Args:
            query: User's natural language query
            data_context: Context about available data (columns, types, sample)
            analysis_type: Optional type hint (visualization, statistics, ml, etc.)

        Returns:
            Generated Python code as string
        """
        prompt = self._build_prompt(query, data_context, analysis_type)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.2,  # Lower temperature for code generation
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            code = self._extract_code(response.content[0].text)
            return code

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise

    def _build_prompt(self,
                     query: str,
                     data_context: Dict[str, Any],
                     analysis_type: Optional[str]) -> str:
        """Build prompt for code generation"""

        # Extract data context information
        columns = data_context.get('columns', [])
        dtypes = data_context.get('dtypes', {})
        shape = data_context.get('shape', (0, 0))
        sample_data = data_context.get('sample', None)

        prompt = f"""You are a Python data analysis code generator. Generate a complete, production-ready Python script that performs the requested analysis.

# User Query
{query}

# Available Data Context
The data is available as a pandas DataFrame loaded from '/sandbox/data/data.pkl'.

**Shape**: {shape[0]} rows, {shape[1]} columns

**Columns and Types**:
{self._format_columns(columns, dtypes)}

{self._format_sample(sample_data) if sample_data else ""}

# Code Requirements

1. **Load Data**: Load the DataFrame from pickle file
2. **Analysis**: Perform the analysis requested in the query
3. **Outputs**: Save results to `/sandbox/outputs/` directory:
   - Visualizations as PNG or HTML files
   - Metrics/statistics as JSON
   - Insights as text file
4. **Error Handling**: Include try-except blocks for robustness
5. **Comments**: Add clear comments explaining the analysis
6. **Libraries**: Use pandas, numpy, matplotlib, seaborn, plotly, scikit-learn, scipy, statsmodels as needed

# Output Format Requirements

- **Plots**: Save to `/sandbox/outputs/plot_*.png` or `/sandbox/outputs/plot_*.html`
- **Metrics**: Save to `/sandbox/outputs/metrics.json`
- **Insights**: Save to `/sandbox/outputs/insights.txt`
- **Data**: Save processed data to `/sandbox/outputs/results.csv` if applicable

# Code Template

```python
import pickle
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Visualization imports (use as needed)
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Set matplotlib backend
plt.switch_backend('Agg')

# Output directory
OUTPUT_DIR = Path('/sandbox/outputs')

def main():
    try:
        # Load data
        with open('/sandbox/data/data.pkl', 'rb') as f:
            df = pickle.load(f)

        print(f"Loaded data: {{df.shape[0]}} rows, {{df.shape[1]}} columns")

        # YOUR ANALYSIS CODE HERE

        # Save outputs
        # metrics = {{"metric1": value1, "metric2": value2}}
        # with open(OUTPUT_DIR / 'metrics.json', 'w') as f:
        #     json.dump(metrics, f, indent=2)

        print("Analysis complete!")

    except Exception as e:
        print(f"Error: {{e}}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
```

# Important Guidelines

- Focus on the specific analysis requested
- Generate visualizations that are clear and informative
- Calculate relevant statistical metrics
- Provide natural language insights about findings
- Handle missing data appropriately
- Use efficient pandas operations
- Keep plots publication-quality (proper labels, titles, legends)
- For time series: respect temporal ordering
- For financial data: use appropriate scales and formatting

{f"# Analysis Type Hint\\n{analysis_type}" if analysis_type else ""}

Generate ONLY the Python code, no explanations before or after. The code should be complete and ready to execute.
"""
        return prompt

    def _format_columns(self, columns: List[str], dtypes: Dict[str, str]) -> str:
        """Format columns and types for prompt"""
        if not columns:
            return "No column information available"

        lines = []
        for col in columns:
            dtype = dtypes.get(col, 'unknown')
            lines.append(f"  - `{col}`: {dtype}")

        return "\n".join(lines)

    def _format_sample(self, sample_data: Any) -> str:
        """Format sample data for prompt"""
        return f"""
**Sample Data** (first few rows):
```
{sample_data}
```
"""

    def _extract_code(self, response_text: str) -> str:
        """Extract Python code from Claude's response"""
        # Remove markdown code blocks if present
        code = response_text.strip()

        # Strip markdown code fences
        if code.startswith('```python'):
            code = code[len('```python'):].strip()
        elif code.startswith('```'):
            code = code[len('```'):].strip()

        if code.endswith('```'):
            code = code[:-len('```')].strip()

        return code

    async def generate_insights(self,
                               query: str,
                               outputs: Dict[str, Any],
                               execution_result: Any) -> str:
        """
        Generate natural language insights from analysis results

        Args:
            query: Original user query
            outputs: Generated outputs (plots, metrics, data)
            execution_result: Execution result object

        Returns:
            Natural language insights
        """
        # Extract metrics if available
        metrics = outputs.get('metrics.json', {})
        insights_file = outputs.get('insights.txt', '')

        # If insights were already generated, return them
        if insights_file:
            return insights_file

        # Otherwise, generate insights from metrics
        prompt = f"""You are a data analyst providing insights to a user.

# User Query
{query}

# Analysis Results

**Execution Status**: {'Success' if execution_result.success else 'Failed'}
**Execution Time**: {execution_result.execution_time:.2f} seconds

**Generated Outputs**:
{', '.join(outputs.keys())}

**Metrics**:
```json
{json.dumps(metrics, indent=2) if metrics else 'No metrics generated'}
```

**Console Output**:
```
{execution_result.stdout[-1000:]}  # Last 1000 chars
```

# Task

Provide a clear, concise summary of the analysis results in 3-5 bullet points. Focus on:
1. What was analyzed
2. Key findings and metrics
3. Notable patterns or insights
4. Recommendations or next steps (if applicable)

Be specific and reference actual numbers from the metrics.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return "Could not generate insights from the analysis results."


# Convenience function
async def generate_analysis_code(
    query: str,
    data_context: Dict[str, Any],
    analysis_type: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Generate Python analysis code (convenience function)

    Args:
        query: User's analysis request
        data_context: Information about available data
        analysis_type: Optional type hint
        api_key: Anthropic API key

    Returns:
        Python code as string
    """
    generator = CodeGenerator(api_key=api_key)
    return await generator.generate(query, data_context, analysis_type)
