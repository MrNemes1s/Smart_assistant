"""
Visualization Helpers for Analysis Scripts
Utility functions to be used within generated analysis code
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Any, List, Optional


def setup_plot_style(style: str = 'seaborn-v0_8-darkgrid'):
    """
    Set up plot styling for consistent, professional visualizations

    Args:
        style: Matplotlib style to use
    """
    try:
        plt.style.use(style)
    except:
        plt.style.use('default')

    # Set default font sizes
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 16

    # Set color palette
    sns.set_palette("husl")


def save_plot(filename: str, dpi: int = 150, bbox_inches: str = 'tight'):
    """
    Save current matplotlib figure

    Args:
        filename: Output filename (should be in /sandbox/outputs/)
        dpi: Resolution in dots per inch
        bbox_inches: Bounding box setting
    """
    plt.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
    plt.close()


def create_financial_time_series(
    dates: Any,
    values: Any,
    title: str = "Time Series",
    ylabel: str = "Value",
    benchmark_values: Optional[Any] = None,
    benchmark_label: str = "Benchmark"
) -> None:
    """
    Create a financial time series plot

    Args:
        dates: Date values (x-axis)
        values: Price/value data (y-axis)
        title: Plot title
        ylabel: Y-axis label
        benchmark_values: Optional benchmark data to overlay
        benchmark_label: Label for benchmark
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, values, label='Portfolio', linewidth=2, color='#2E86AB')

    if benchmark_values is not None:
        ax.plot(dates, benchmark_values, label=benchmark_label,
                linewidth=2, linestyle='--', color='#A23B72', alpha=0.7)

    ax.set_xlabel('Date')
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format x-axis for dates
    fig.autofmt_xdate()

    plt.tight_layout()


def create_returns_distribution(
    returns: Any,
    title: str = "Returns Distribution",
    bins: int = 50
) -> None:
    """
    Create histogram of returns with normal distribution overlay

    Args:
        returns: Array of return values
        title: Plot title
        bins: Number of histogram bins
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Histogram
    n, bins_edges, patches = ax.hist(returns, bins=bins, density=True,
                                      alpha=0.7, color='skyblue',
                                      edgecolor='black', linewidth=0.5)

    # Fit normal distribution
    mu = np.mean(returns)
    sigma = np.std(returns)
    x = np.linspace(returns.min(), returns.max(), 100)
    from scipy import stats
    ax.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2,
            label=f'Normal (μ={mu:.3f}, σ={sigma:.3f})')

    # Add mean line
    ax.axvline(mu, color='green', linestyle='--', linewidth=2, label=f'Mean: {mu:.3f}')

    ax.set_xlabel('Returns')
    ax.set_ylabel('Density')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()


def create_correlation_heatmap(
    correlation_matrix: Any,
    title: str = "Correlation Matrix",
    cmap: str = 'coolwarm'
) -> None:
    """
    Create correlation heatmap

    Args:
        correlation_matrix: Correlation matrix (pandas DataFrame or numpy array)
        title: Plot title
        cmap: Color map to use
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(correlation_matrix,
                annot=True,
                fmt='.2f',
                cmap=cmap,
                center=0,
                square=True,
                linewidths=1,
                cbar_kws={"shrink": 0.8},
                ax=ax)

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()


def create_portfolio_allocation(
    labels: List[str],
    values: List[float],
    title: str = "Portfolio Allocation",
    explode: Optional[List[float]] = None
) -> None:
    """
    Create pie chart for portfolio allocation

    Args:
        labels: Asset labels
        values: Allocation values (percentages or amounts)
        title: Plot title
        explode: Optional explode values for pie slices
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    colors = sns.color_palette('pastel')[0:len(labels)]

    if explode is None:
        explode = [0.05] * len(labels)

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        explode=explode
    )

    # Enhance text
    for text in texts:
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()


def format_financial_axis(ax, axis: str = 'y', prefix: str = '$', decimals: int = 0):
    """
    Format axis for financial values

    Args:
        ax: Matplotlib axis object
        axis: Which axis to format ('x', 'y', or 'both')
        prefix: Currency prefix
        decimals: Number of decimal places
    """
    from matplotlib.ticker import FuncFormatter

    def financial_formatter(x, pos):
        if abs(x) >= 1e9:
            return f'{prefix}{x/1e9:.{decimals}f}B'
        elif abs(x) >= 1e6:
            return f'{prefix}{x/1e6:.{decimals}f}M'
        elif abs(x) >= 1e3:
            return f'{prefix}{x/1e3:.{decimals}f}K'
        else:
            return f'{prefix}{x:.{decimals}f}'

    formatter = FuncFormatter(financial_formatter)

    if axis in ['y', 'both']:
        ax.yaxis.set_major_formatter(formatter)
    if axis in ['x', 'both']:
        ax.xaxis.set_major_formatter(formatter)


# Helper constants for colors
COLORS = {
    'profit': '#2ECC71',
    'loss': '#E74C3C',
    'neutral': '#95A5A6',
    'primary': '#3498DB',
    'secondary': '#9B59B6',
    'warning': '#F39C12',
    'info': '#1ABC9C'
}


def get_color_for_value(value: float, positive_color: str = None, negative_color: str = None) -> str:
    """
    Get color based on value sign

    Args:
        value: Numeric value
        positive_color: Color for positive values
        negative_color: Color for negative values

    Returns:
        Color string
    """
    if positive_color is None:
        positive_color = COLORS['profit']
    if negative_color is None:
        negative_color = COLORS['loss']

    return positive_color if value >= 0 else negative_color
