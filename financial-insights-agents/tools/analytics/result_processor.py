"""
Result Processor for Sandbox Execution Outputs
Processes and formats analysis results, visualizations, and insights
"""
import base64
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Structured analysis result"""
    success: bool
    query: str
    insights: str
    visualizations: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    data_outputs: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None
    raw_output: Optional[str] = None


class ResultProcessor:
    """Processes sandbox execution results into structured outputs"""

    def process(self,
                query: str,
                execution_result: Any,
                insights: Optional[str] = None) -> AnalysisResult:
        """
        Process execution result into structured format

        Args:
            query: Original user query
            execution_result: ExecutionResult from sandbox
            insights: Optional generated insights

        Returns:
            AnalysisResult with structured data
        """
        if not execution_result.success:
            return AnalysisResult(
                success=False,
                query=query,
                insights=f"Analysis failed: {execution_result.error or 'Unknown error'}",
                visualizations=[],
                metrics={},
                data_outputs={},
                execution_time=execution_result.execution_time,
                error=execution_result.error,
                raw_output=execution_result.stderr
            )

        # Process outputs
        visualizations = self._extract_visualizations(execution_result.outputs)
        metrics = self._extract_metrics(execution_result.outputs)
        data_outputs = self._extract_data_outputs(execution_result.outputs)

        # Use insights from file or provided parameter
        final_insights = insights or self._extract_insights(execution_result.outputs)

        return AnalysisResult(
            success=True,
            query=query,
            insights=final_insights,
            visualizations=visualizations,
            metrics=metrics,
            data_outputs=data_outputs,
            execution_time=execution_result.execution_time,
            raw_output=execution_result.stdout
        )

    def _extract_visualizations(self, outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract visualization outputs"""
        visualizations = []

        for filename, content in outputs.items():
            # PNG images
            if filename.endswith('.png'):
                visualizations.append({
                    'type': 'image',
                    'format': 'png',
                    'filename': filename,
                    'data': base64.b64encode(content).decode('utf-8') if isinstance(content, bytes) else content,
                    'title': self._filename_to_title(filename)
                })

            # HTML plots (plotly, etc.)
            elif filename.endswith('.html'):
                visualizations.append({
                    'type': 'html',
                    'format': 'html',
                    'filename': filename,
                    'data': content,
                    'title': self._filename_to_title(filename)
                })

        return visualizations

    def _extract_metrics(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from outputs"""
        metrics = {}

        # Look for metrics.json
        if 'metrics.json' in outputs:
            try:
                if isinstance(outputs['metrics.json'], dict):
                    metrics = outputs['metrics.json']
                else:
                    metrics = json.loads(outputs['metrics.json'])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse metrics: {e}")

        # Look for other JSON files
        for filename, content in outputs.items():
            if filename.endswith('.json') and filename != 'metrics.json':
                try:
                    if isinstance(content, dict):
                        metrics[filename.replace('.json', '')] = content
                    else:
                        metrics[filename.replace('.json', '')] = json.loads(content)
                except json.JSONDecodeError:
                    pass

        return metrics

    def _extract_data_outputs(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data outputs (CSV, text files)"""
        data_outputs = {}

        for filename, content in outputs.items():
            # CSV files
            if filename.endswith('.csv'):
                data_outputs[filename] = {
                    'type': 'csv',
                    'content': content
                }

            # Text files (excluding insights.txt which is handled separately)
            elif filename.endswith('.txt') and filename != 'insights.txt':
                data_outputs[filename] = {
                    'type': 'text',
                    'content': content
                }

        return data_outputs

    def _extract_insights(self, outputs: Dict[str, Any]) -> str:
        """Extract insights from outputs"""
        if 'insights.txt' in outputs:
            return outputs['insights.txt']

        return "No insights generated. Check the visualizations and metrics for analysis results."

    def _filename_to_title(self, filename: str) -> str:
        """Convert filename to readable title"""
        # Remove extension
        name = filename.rsplit('.', 1)[0]

        # Remove common prefixes
        for prefix in ['plot_', 'chart_', 'fig_', 'graph_']:
            if name.startswith(prefix):
                name = name[len(prefix):]

        # Replace underscores with spaces and title case
        return name.replace('_', ' ').title()

    def format_for_chat(self, result: AnalysisResult) -> str:
        """
        Format analysis result for chat interface

        Args:
            result: AnalysisResult to format

        Returns:
            Markdown-formatted string for chat display
        """
        if not result.success:
            return f"""## Analysis Failed

**Error**: {result.error or 'Unknown error'}

**Output**:
```
{result.raw_output}
```
"""

        output = f"""## Analysis Results

{result.insights}

"""

        # Add metrics section
        if result.metrics:
            output += "### Key Metrics\n\n"
            for key, value in result.metrics.items():
                if isinstance(value, dict):
                    output += f"**{key}**:\n"
                    for k, v in value.items():
                        output += f"  - {k}: {self._format_value(v)}\n"
                else:
                    output += f"- **{key}**: {self._format_value(value)}\n"
            output += "\n"

        # Add visualization references
        if result.visualizations:
            output += f"### Visualizations\n\n"
            output += f"Generated {len(result.visualizations)} visualization(s):\n"
            for i, viz in enumerate(result.visualizations, 1):
                output += f"{i}. {viz['title']} ({viz['format'].upper()})\n"
            output += "\n"

        # Add execution info
        output += f"*Execution time: {result.execution_time:.2f}s*\n"

        return output

    def _format_value(self, value: Any) -> str:
        """Format a value for display"""
        if isinstance(value, float):
            # Format floats nicely
            if abs(value) < 0.01 or abs(value) > 10000:
                return f"{value:.2e}"
            else:
                return f"{value:.2f}"
        elif isinstance(value, (list, tuple)) and len(value) > 5:
            # Truncate long lists
            return f"[{', '.join(map(str, value[:5]))}, ... ({len(value)} items)]"
        else:
            return str(value)


# Convenience function
def process_analysis_result(
    query: str,
    execution_result: Any,
    insights: Optional[str] = None
) -> AnalysisResult:
    """
    Process analysis result (convenience function)

    Args:
        query: Original query
        execution_result: Execution result from sandbox
        insights: Optional insights

    Returns:
        Structured AnalysisResult
    """
    processor = ResultProcessor()
    return processor.process(query, execution_result, insights)
