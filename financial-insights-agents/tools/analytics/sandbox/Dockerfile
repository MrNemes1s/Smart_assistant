# Python Analysis Sandbox - Secure Docker Environment
FROM python:3.11-slim

# Set working directory
WORKDIR /sandbox

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python data science stack
RUN pip install --no-cache-dir \
    pandas==2.1.4 \
    numpy==1.26.2 \
    scipy==1.11.4 \
    scikit-learn==1.3.2 \
    statsmodels==0.14.1 \
    matplotlib==3.8.2 \
    seaborn==0.13.0 \
    plotly==5.18.0 \
    kaleido==0.2.1

# Create non-root user for security
RUN useradd -m -u 1000 sandboxuser && \
    chown -R sandboxuser:sandboxuser /sandbox

# Switch to non-root user
USER sandboxuser

# Create directories for data and outputs
RUN mkdir -p /sandbox/data /sandbox/outputs

# Set resource limits via environment
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

# Default command (will be overridden)
CMD ["python", "-u", "script.py"]
