"""
Financial Analysis Code Templates
Pre-built templates for common financial analysis patterns
"""

PORTFOLIO_PERFORMANCE = """
# Portfolio Performance Analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

OUTPUT_DIR = Path('/sandbox/outputs')

# Load data
with open('/sandbox/data/data.pkl', 'rb') as f:
    df = pickle.load(f)

# Calculate returns
df['returns'] = df['portfolio_value'].pct_change()

# Calculate cumulative returns
df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1

# Calculate metrics
total_return = df['cumulative_returns'].iloc[-1]
annualized_return = (1 + total_return) ** (252 / len(df)) - 1
volatility = df['returns'].std() * np.sqrt(252)
sharpe_ratio = annualized_return / volatility if volatility > 0 else 0

# Max drawdown
cumulative = df['cumulative_returns'] + 1
running_max = cumulative.expanding().max()
drawdown = (cumulative - running_max) / running_max
max_drawdown = drawdown.min()

# Save metrics
metrics = {
    'total_return': float(total_return),
    'annualized_return': float(annualized_return),
    'volatility': float(volatility),
    'sharpe_ratio': float(sharpe_ratio),
    'max_drawdown': float(max_drawdown)
}

with open(OUTPUT_DIR / 'metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# Generate plot
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['cumulative_returns'] * 100, label='Portfolio', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Cumulative Returns (%)')
plt.title('Portfolio Performance Over Time')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot_performance.png', dpi=150, bbox_inches='tight')
plt.close()

# Insights
insights = f'''Portfolio Performance Analysis:
• Total Return: {total_return*100:.2f}%
• Annualized Return: {annualized_return*100:.2f}%
• Volatility (Annual): {volatility*100:.2f}%
• Sharpe Ratio: {sharpe_ratio:.2f}
• Maximum Drawdown: {max_drawdown*100:.2f}%
'''

with open(OUTPUT_DIR / 'insights.txt', 'w') as f:
    f.write(insights)
"""

CORRELATION_ANALYSIS = """
# Correlation and Relationship Analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

OUTPUT_DIR = Path('/sandbox/outputs')

# Load data
with open('/sandbox/data/data.pkl', 'rb') as f:
    df = pickle.load(f)

# Calculate correlation matrix
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlation_matrix = df[numeric_cols].corr()

# Save metrics
metrics = {
    'correlation_matrix': correlation_matrix.to_dict(),
    'highest_correlations': []
}

# Find highest correlations (excluding diagonal)
for i in range(len(correlation_matrix)):
    for j in range(i+1, len(correlation_matrix)):
        metrics['highest_correlations'].append({
            'var1': correlation_matrix.index[i],
            'var2': correlation_matrix.columns[j],
            'correlation': float(correlation_matrix.iloc[i, j])
        })

metrics['highest_correlations'].sort(key=lambda x: abs(x['correlation']), reverse=True)
metrics['highest_correlations'] = metrics['highest_correlations'][:5]

with open(OUTPUT_DIR / 'metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# Generate heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot_correlation.png', dpi=150, bbox_inches='tight')
plt.close()

# Insights
top_corr = metrics['highest_correlations'][0]
insights = f'''Correlation Analysis Results:
• Analyzed {len(numeric_cols)} numeric variables
• Strongest correlation: {top_corr['var1']} vs {top_corr['var2']} ({top_corr['correlation']:.3f})
• See heatmap for full correlation matrix
'''

with open(OUTPUT_DIR / 'insights.txt', 'w') as f:
    f.write(insights)
"""

DISTRIBUTION_ANALYSIS = """
# Distribution and Statistical Analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import json
from pathlib import Path

OUTPUT_DIR = Path('/sandbox/outputs')

# Load data
with open('/sandbox/data/data.pkl', 'rb') as f:
    df = pickle.load(f)

# Select numeric column for analysis (first numeric column)
numeric_cols = df.select_dtypes(include=[np.number]).columns
target_col = numeric_cols[0]  # Modify based on query

data = df[target_col].dropna()

# Calculate statistics
mean = data.mean()
median = data.median()
std = data.std()
skewness = stats.skew(data)
kurtosis = stats.kurtosis(data)

# Normality test
_, p_value = stats.normaltest(data)
is_normal = p_value > 0.05

# Percentiles
percentiles = {
    '25th': data.quantile(0.25),
    '50th': data.quantile(0.50),
    '75th': data.quantile(0.75),
    '90th': data.quantile(0.90),
    '95th': data.quantile(0.95)
}

# Save metrics
metrics = {
    'column': target_col,
    'mean': float(mean),
    'median': float(median),
    'std': float(std),
    'skewness': float(skewness),
    'kurtosis': float(kurtosis),
    'normality_p_value': float(p_value),
    'is_normal': bool(is_normal),
    'percentiles': {k: float(v) for k, v in percentiles.items()}
}

with open(OUTPUT_DIR / 'metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# Generate plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Histogram
axes[0, 0].hist(data, bins=50, edgecolor='black', alpha=0.7)
axes[0, 0].axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
axes[0, 0].axvline(median, color='green', linestyle='--', label=f'Median: {median:.2f}')
axes[0, 0].set_xlabel(target_col)
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Distribution')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Box plot
axes[0, 1].boxplot(data, vert=True)
axes[0, 1].set_ylabel(target_col)
axes[0, 1].set_title('Box Plot')
axes[0, 1].grid(True, alpha=0.3)

# Q-Q plot
stats.probplot(data, dist="norm", plot=axes[1, 0])
axes[1, 0].set_title('Q-Q Plot (Normality Check)')

# Density plot
axes[1, 1].hist(data, bins=50, density=True, alpha=0.5, label='Data')
# Fit normal distribution
mu, sigma = data.mean(), data.std()
x = np.linspace(data.min(), data.max(), 100)
axes[1, 1].plot(x, stats.norm.pdf(x, mu, sigma), 'r-', label='Normal fit')
axes[1, 1].set_xlabel(target_col)
axes[1, 1].set_ylabel('Density')
axes[1, 1].set_title('Density Plot with Normal Fit')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# Insights
insights = f'''Distribution Analysis for {target_col}:
• Mean: {mean:.2f}, Median: {median:.2f}, Std Dev: {std:.2f}
• Skewness: {skewness:.2f} ({'right' if skewness > 0 else 'left'} skewed)
• Distribution is {'approximately normal' if is_normal else 'not normal'} (p={p_value:.4f})
• 90th percentile: {percentiles['90th']:.2f}
'''

with open(OUTPUT_DIR / 'insights.txt', 'w') as f:
    f.write(insights)
"""

TIME_SERIES_ANALYSIS = """
# Time Series Analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from statsmodels.tsa.seasonal import seasonal_decompose

OUTPUT_DIR = Path('/sandbox/outputs')

# Load data
with open('/sandbox/data/data.pkl', 'rb') as f:
    df = pickle.load(f)

# Ensure datetime index
date_col = df.select_dtypes(include=['datetime64']).columns[0]
df = df.set_index(date_col).sort_index()

# Select numeric column
numeric_cols = df.select_dtypes(include=[np.number]).columns
target_col = numeric_cols[0]
series = df[target_col]

# Calculate rolling statistics
window = min(30, len(series) // 4)
rolling_mean = series.rolling(window=window).mean()
rolling_std = series.rolling(window=window).std()

# Calculate trends
pct_change = series.pct_change()
mean_daily_change = pct_change.mean()
volatility = pct_change.std()

# Save metrics
metrics = {
    'column': target_col,
    'mean_value': float(series.mean()),
    'mean_daily_change': float(mean_daily_change),
    'volatility': float(volatility),
    'min_value': float(series.min()),
    'max_value': float(series.max()),
    'start_value': float(series.iloc[0]),
    'end_value': float(series.iloc[-1]),
    'total_change_pct': float((series.iloc[-1] / series.iloc[0] - 1) * 100)
}

with open(OUTPUT_DIR / 'metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# Generate plots
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# Time series with rolling mean
axes[0].plot(series.index, series, label='Actual', alpha=0.7)
axes[0].plot(rolling_mean.index, rolling_mean, label=f'{window}-day MA', linewidth=2)
axes[0].fill_between(series.index,
                      rolling_mean - rolling_std,
                      rolling_mean + rolling_std,
                      alpha=0.2, label='±1 Std Dev')
axes[0].set_xlabel('Date')
axes[0].set_ylabel(target_col)
axes[0].set_title('Time Series with Rolling Statistics')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Daily changes
axes[1].bar(pct_change.index, pct_change * 100, alpha=0.7)
axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Daily Change (%)')
axes[1].set_title('Daily Percentage Changes')
axes[1].grid(True, alpha=0.3)

# Cumulative returns
cumulative = (1 + pct_change).cumprod()
axes[2].plot(cumulative.index, (cumulative - 1) * 100)
axes[2].set_xlabel('Date')
axes[2].set_ylabel('Cumulative Return (%)')
axes[2].set_title('Cumulative Returns')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'plot_timeseries.png', dpi=150, bbox_inches='tight')
plt.close()

# Insights
insights = f'''Time Series Analysis for {target_col}:
• Total change: {metrics['total_change_pct']:.2f}%
• Average daily change: {mean_daily_change*100:.3f}%
• Volatility: {volatility*100:.2f}%
• Value range: {metrics['min_value']:.2f} to {metrics['max_value']:.2f}
'''

with open(OUTPUT_DIR / 'insights.txt', 'w') as f:
    f.write(insights)
"""

TEMPLATES = {
    'portfolio_performance': PORTFOLIO_PERFORMANCE,
    'correlation': CORRELATION_ANALYSIS,
    'distribution': DISTRIBUTION_ANALYSIS,
    'time_series': TIME_SERIES_ANALYSIS
}


def get_template(template_name: str) -> str:
    """Get analysis template by name"""
    return TEMPLATES.get(template_name, "")


def list_templates() -> list:
    """List available templates"""
    return list(TEMPLATES.keys())
