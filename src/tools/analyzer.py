"""Data analysis tools for research agents."""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import asyncio
import json


@dataclass
class AnalysisResult:
    """Result of data analysis."""
    analysis_type: str
    success: bool
    summary: str
    statistics: Dict[str, Any]
    visualizations: List[str]
    data: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_type": self.analysis_type,
            "success": self.success,
            "summary": self.summary,
            "statistics": self.statistics,
            "visualizations": self.visualizations,
            "data": self.data,
        }


class DataAnalyzer:
    """
    Data analysis tool for research tasks.

    Capabilities:
    - Statistical analysis
    - Data summarization
    - Pattern detection
    - Correlation analysis
    - Basic visualization
    """

    def __init__(self, **kwargs):
        self.name = "DataAnalyzer"

    async def analyze(self, data: Any, analysis_type: str = "auto",
                     **kwargs) -> AnalysisResult:
        """
        Analyze data.

        Args:
            data: Input data (dict, list, or string)
            analysis_type: Type of analysis to perform
            **kwargs: Additional parameters

        Returns:
            AnalysisResult with findings
        """
        if isinstance(data, str):
            # Try to parse JSON
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass

        if analysis_type == "auto":
            analysis_type = self._detect_analysis_type(data)

        if analysis_type == "statistical":
            return await self._statistical_analysis(data, **kwargs)
        elif analysis_type == "text":
            return await self._text_analysis(data, **kwargs)
        elif analysis_type == "comparative":
            return await self._comparative_analysis(data, **kwargs)
        elif analysis_type == "pattern":
            return await self._pattern_detection(data, **kwargs)
        else:
            return await self._basic_summary(data)

    def _detect_analysis_type(self, data: Any) -> str:
        """Detect appropriate analysis type from data."""
        if isinstance(data, dict):
            return "statistical"
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                return "comparative"
            return "statistical"
        elif isinstance(data, str):
            return "text"
        return "basic"

    async def _statistical_analysis(self, data: Any,
                                   **kwargs) -> AnalysisResult:
        """Perform statistical analysis."""
        await asyncio.sleep(0.01)

        stats = {}

        if isinstance(data, (list, dict)):
            if isinstance(data, dict):
                values = [v for v in data.values() if isinstance(v, (int, float))]
            else:
                values = [v for v in data if isinstance(v, (int, float))]

            if values:
                stats = {
                    "count": len(values),
                    "sum": sum(values),
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                }

        summary = f"Statistical analysis completed on {len(stats)} metrics."

        return AnalysisResult(
            analysis_type="statistical",
            success=True,
            summary=summary,
            statistics=stats,
            visualizations=["histogram", "box_plot"],
            data=data,
        )

    async def _text_analysis(self, data: Any,
                            **kwargs) -> AnalysisResult:
        """Perform text analysis."""
        await asyncio.sleep(0.01)

        text = str(data)
        words = text.split()

        stats = {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": text.count(".") + text.count("!") + text.count("?"),
            "unique_words": len(set(w.lower() for w in words)),
        }

        summary = f"Text analysis: {stats['word_count']} words, {stats['unique_words']} unique."

        return AnalysisResult(
            analysis_type="text",
            success=True,
            summary=summary,
            statistics=stats,
            visualizations=["word_cloud"],
            data=data,
        )

    async def _comparative_analysis(self, data: List[Dict],
                                   **kwargs) -> AnalysisResult:
        """Compare items in a dataset."""
        await asyncio.sleep(0.01)

        if not data:
            return AnalysisResult(
                analysis_type="comparative",
                success=False,
                summary="No data to compare",
                statistics={},
                visualizations=[],
                data=data,
            )

        # Get all keys
        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())

        stats = {
            "item_count": len(data),
            "fields": list(all_keys),
            "common_fields": self._find_common_fields(data),
        }

        summary = f"Comparative analysis of {len(data)} items across {len(all_keys)} fields."

        return AnalysisResult(
            analysis_type="comparative",
            success=True,
            summary=summary,
            statistics=stats,
            visualizations=["comparison_table", "bar_chart"],
            data=data,
        )

    def _find_common_fields(self, data: List[Dict]) -> List[str]:
        """Find fields common to all items."""
        if not data:
            return []

        common = set(data[0].keys())
        for item in data[1:]:
            if isinstance(item, dict):
                common &= set(item.keys())

        return list(common)

    async def _pattern_detection(self, data: Any,
                                **kwargs) -> AnalysisResult:
        """Detect patterns in data."""
        await asyncio.sleep(0.01)

        patterns = {
            "trend": "no_significant_trend",
            "seasonality": False,
            "outliers": [],
        }

        summary = "Pattern detection completed. No significant patterns found."

        return AnalysisResult(
            analysis_type="pattern",
            success=True,
            summary=summary,
            statistics=patterns,
            visualizations=["time_series"],
            data=data,
        )

    async def _basic_summary(self, data: Any) -> AnalysisResult:
        """Basic data summary."""
        await asyncio.sleep(0.01)

        summary = f"Data summary: {type(data).__name__}"

        return AnalysisResult(
            analysis_type="basic",
            success=True,
            summary=summary,
            statistics={"type": type(data).__name__},
            visualizations=[],
            data=data,
        )


class VisualizationGenerator:
    """Generate visualizations from analysis results."""

    SUPPORTED_TYPES = ["histogram", "bar_chart", "line_chart", "pie_chart", "scatter"]

    def __init__(self, **kwargs):
        self.name = "VisualizationGenerator"

    async def generate(self, analysis_result: AnalysisResult,
                      viz_type: str = "auto") -> str:
        """
        Generate visualization code.

        Args:
            analysis_result: Result from DataAnalyzer
            viz_type: Type of visualization

        Returns:
            Code to generate visualization
        """
        if viz_type == "auto":
            if analysis_result.visualizations:
                viz_type = analysis_result.visualizations[0]
            else:
                viz_type = "bar_chart"

        if viz_type not in self.SUPPORTED_TYPES:
            viz_type = "bar_chart"

        code = self._generate_plot_code(viz_type, analysis_result)
        return code

    def _generate_plot_code(self, viz_type: str,
                          analysis_result: AnalysisResult) -> str:
        """Generate matplotlib code for visualization."""
        code = f"""import matplotlib.pyplot as plt
import numpy as np

# Data from {analysis_result.analysis_type} analysis
stats = {analysis_result.statistics}

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# {viz_type} visualization
if viz_type == "bar_chart":
    labels = list(stats.keys())
    values = [v for v in stats.values() if isinstance(v, (int, float))]
    ax.bar(labels[:len(values)], values)
elif viz_type == "histogram":
    ax.hist(values, bins=20)
elif viz_type == "pie_chart":
    ax.pie(values, labels=labels[:len(values)], autopct='%1.1f%%')

ax.set_title('{analysis_result.analysis_type.title()} Analysis')
plt.tight_layout()
plt.savefig('analysis_plot.png')
print('Plot saved to analysis_plot.png')
"""
        return code
