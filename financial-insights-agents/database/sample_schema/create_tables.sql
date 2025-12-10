-- Financial Insights Database Schema
-- Sample database for multi-agent financial analysis system

-- Drop tables if they exist (for clean re-creation)
IF OBJECT_ID('dbo.transactions', 'U') IS NOT NULL DROP TABLE dbo.transactions;
IF OBJECT_ID('dbo.holdings', 'U') IS NOT NULL DROP TABLE dbo.holdings;
IF OBJECT_ID('dbo.prices', 'U') IS NOT NULL DROP TABLE dbo.prices;
IF OBJECT_ID('dbo.benchmarks', 'U') IS NOT NULL DROP TABLE dbo.benchmarks;
IF OBJECT_ID('dbo.portfolios', 'U') IS NOT NULL DROP TABLE dbo.portfolios;
GO

-- Portfolios table
CREATE TABLE dbo.portfolios (
    portfolio_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    strategy NVARCHAR(50) NOT NULL,
    risk_profile NVARCHAR(20) CHECK (risk_profile IN ('conservative', 'moderate', 'aggressive')),
    inception_date DATE NOT NULL,
    initial_capital DECIMAL(18, 2) NOT NULL,
    current_value DECIMAL(18, 2),
    owner_name NVARCHAR(100),
    description NVARCHAR(500),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
GO

-- Indexes for portfolios
CREATE INDEX idx_portfolios_strategy ON dbo.portfolios(strategy);
CREATE INDEX idx_portfolios_risk_profile ON dbo.portfolios(risk_profile);
CREATE INDEX idx_portfolios_is_active ON dbo.portfolios(is_active);
GO

-- Holdings table (current positions)
CREATE TABLE dbo.holdings (
    holding_id INT PRIMARY KEY IDENTITY(1,1),
    portfolio_id INT NOT NULL,
    symbol NVARCHAR(10) NOT NULL,
    asset_type NVARCHAR(20) CHECK (asset_type IN ('stock', 'bond', 'etf', 'mutual_fund', 'crypto', 'cash')),
    quantity DECIMAL(18, 6) NOT NULL,
    purchase_date DATE NOT NULL,
    purchase_price DECIMAL(18, 4) NOT NULL,
    current_price DECIMAL(18, 4),
    cost_basis DECIMAL(18, 2) COMPUTED (quantity * purchase_price) PERSISTED,
    current_value DECIMAL(18, 2) COMPUTED (quantity * ISNULL(current_price, purchase_price)) PERSISTED,
    unrealized_gain_loss DECIMAL(18, 2) COMPUTED (quantity * (ISNULL(current_price, purchase_price) - purchase_price)) PERSISTED,
    sector NVARCHAR(50),
    country NVARCHAR(50),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(portfolio_id) ON DELETE CASCADE
);
GO

-- Indexes for holdings
CREATE INDEX idx_holdings_portfolio ON dbo.holdings(portfolio_id);
CREATE INDEX idx_holdings_symbol ON dbo.holdings(symbol);
CREATE INDEX idx_holdings_asset_type ON dbo.holdings(asset_type);
CREATE INDEX idx_holdings_sector ON dbo.holdings(sector);
GO

-- Transactions table (historical trades)
CREATE TABLE dbo.transactions (
    transaction_id INT PRIMARY KEY IDENTITY(1,1),
    portfolio_id INT NOT NULL,
    symbol NVARCHAR(10) NOT NULL,
    transaction_type NVARCHAR(10) CHECK (transaction_type IN ('buy', 'sell', 'dividend', 'split', 'transfer')),
    quantity DECIMAL(18, 6) NOT NULL,
    price DECIMAL(18, 4) NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_time TIME DEFAULT CONVERT(TIME, GETDATE()),
    fees DECIMAL(18, 2) DEFAULT 0,
    tax DECIMAL(18, 2) DEFAULT 0,
    total_amount DECIMAL(18, 2) COMPUTED (
        CASE
            WHEN transaction_type IN ('buy', 'transfer') THEN quantity * price + fees + tax
            WHEN transaction_type = 'sell' THEN quantity * price - fees - tax
            ELSE quantity * price
        END
    ) PERSISTED,
    notes NVARCHAR(500),
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(portfolio_id) ON DELETE CASCADE
);
GO

-- Indexes for transactions
CREATE INDEX idx_transactions_portfolio ON dbo.transactions(portfolio_id);
CREATE INDEX idx_transactions_symbol ON dbo.transactions(symbol);
CREATE INDEX idx_transactions_date ON dbo.transactions(transaction_date);
CREATE INDEX idx_transactions_type ON dbo.transactions(transaction_type);
GO

-- Prices table (daily market prices)
CREATE TABLE dbo.prices (
    price_id INT PRIMARY KEY IDENTITY(1,1),
    symbol NVARCHAR(10) NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(18, 4) NOT NULL,
    high_price DECIMAL(18, 4) NOT NULL,
    low_price DECIMAL(18, 4) NOT NULL,
    close_price DECIMAL(18, 4) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(18, 4),
    daily_return DECIMAL(10, 6),
    created_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT uc_prices_symbol_date UNIQUE (symbol, price_date)
);
GO

-- Indexes for prices
CREATE INDEX idx_prices_symbol ON dbo.prices(symbol);
CREATE INDEX idx_prices_date ON dbo.prices(price_date);
CREATE INDEX idx_prices_symbol_date ON dbo.prices(symbol, price_date);
GO

-- Benchmarks table (index data for comparison)
CREATE TABLE dbo.benchmarks (
    benchmark_id INT PRIMARY KEY IDENTITY(1,1),
    index_name NVARCHAR(50) NOT NULL,
    price_date DATE NOT NULL,
    index_value DECIMAL(18, 4) NOT NULL,
    daily_return DECIMAL(10, 6),
    volume BIGINT,
    created_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT uc_benchmarks_index_date UNIQUE (index_name, price_date)
);
GO

-- Indexes for benchmarks
CREATE INDEX idx_benchmarks_index ON dbo.benchmarks(index_name);
CREATE INDEX idx_benchmarks_date ON dbo.benchmarks(price_date);
CREATE INDEX idx_benchmarks_index_date ON dbo.benchmarks(index_name, price_date);
GO

-- View: Portfolio Performance Summary
CREATE VIEW dbo.vw_portfolio_performance AS
SELECT
    p.portfolio_id,
    p.name AS portfolio_name,
    p.strategy,
    p.risk_profile,
    p.inception_date,
    p.initial_capital,
    SUM(h.current_value) AS total_current_value,
    SUM(h.cost_basis) AS total_cost_basis,
    SUM(h.unrealized_gain_loss) AS total_unrealized_gain_loss,
    CASE
        WHEN SUM(h.cost_basis) > 0 THEN
            (SUM(h.current_value) - SUM(h.cost_basis)) / SUM(h.cost_basis) * 100
        ELSE 0
    END AS return_percentage,
    COUNT(h.holding_id) AS number_of_holdings,
    DATEDIFF(DAY, p.inception_date, GETDATE()) AS days_since_inception
FROM dbo.portfolios p
LEFT JOIN dbo.holdings h ON p.portfolio_id = h.portfolio_id
WHERE p.is_active = 1
GROUP BY
    p.portfolio_id, p.name, p.strategy, p.risk_profile,
    p.inception_date, p.initial_capital;
GO

-- View: Holdings with Current Prices
CREATE VIEW dbo.vw_holdings_with_prices AS
SELECT
    h.holding_id,
    h.portfolio_id,
    p.name AS portfolio_name,
    h.symbol,
    h.asset_type,
    h.quantity,
    h.purchase_price,
    h.purchase_date,
    h.current_price,
    h.cost_basis,
    h.current_value,
    h.unrealized_gain_loss,
    CASE
        WHEN h.cost_basis > 0 THEN
            (h.unrealized_gain_loss / h.cost_basis) * 100
        ELSE 0
    END AS return_percentage,
    h.sector,
    h.country,
    DATEDIFF(DAY, h.purchase_date, GETDATE()) AS holding_period_days
FROM dbo.holdings h
INNER JOIN dbo.portfolios p ON h.portfolio_id = p.portfolio_id
WHERE p.is_active = 1;
GO

-- View: Sector Allocation
CREATE VIEW dbo.vw_sector_allocation AS
SELECT
    p.portfolio_id,
    p.name AS portfolio_name,
    h.sector,
    COUNT(h.holding_id) AS number_of_holdings,
    SUM(h.current_value) AS sector_value,
    SUM(h.cost_basis) AS sector_cost_basis,
    SUM(h.unrealized_gain_loss) AS sector_unrealized_gain_loss
FROM dbo.portfolios p
INNER JOIN dbo.holdings h ON p.portfolio_id = h.portfolio_id
WHERE p.is_active = 1 AND h.sector IS NOT NULL
GROUP BY p.portfolio_id, p.name, h.sector;
GO

-- Stored Procedure: Calculate Portfolio Returns
CREATE PROCEDURE dbo.sp_calculate_portfolio_returns
    @portfolio_id INT,
    @start_date DATE = NULL,
    @end_date DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Default to last year if dates not provided
    IF @start_date IS NULL SET @start_date = DATEADD(YEAR, -1, GETDATE());
    IF @end_date IS NULL SET @end_date = GETDATE();

    SELECT
        @portfolio_id AS portfolio_id,
        @start_date AS start_date,
        @end_date AS end_date,
        SUM(CASE WHEN t.transaction_type = 'buy' THEN t.total_amount ELSE 0 END) AS total_invested,
        SUM(CASE WHEN t.transaction_type = 'sell' THEN t.total_amount ELSE 0 END) AS total_proceeds,
        SUM(CASE WHEN t.transaction_type = 'dividend' THEN t.total_amount ELSE 0 END) AS total_dividends,
        SUM(CASE WHEN t.transaction_type IN ('buy', 'sell') THEN t.fees ELSE 0 END) AS total_fees,
        COUNT(t.transaction_id) AS transaction_count
    FROM dbo.transactions t
    WHERE t.portfolio_id = @portfolio_id
        AND t.transaction_date BETWEEN @start_date AND @end_date
    GROUP BY t.portfolio_id;
END;
GO

-- Stored Procedure: Update Current Prices
CREATE PROCEDURE dbo.sp_update_holding_prices
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE h
    SET
        h.current_price = p.close_price,
        h.updated_at = GETDATE()
    FROM dbo.holdings h
    INNER JOIN (
        SELECT
            symbol,
            close_price,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY price_date DESC) AS rn
        FROM dbo.prices
    ) p ON h.symbol = p.symbol AND p.rn = 1;

    RETURN @@ROWCOUNT;
END;
GO

-- Grant permissions (adjust as needed)
PRINT 'Database schema created successfully!';
PRINT 'Tables: portfolios, holdings, transactions, prices, benchmarks';
PRINT 'Views: vw_portfolio_performance, vw_holdings_with_prices, vw_sector_allocation';
PRINT 'Procedures: sp_calculate_portfolio_returns, sp_update_holding_prices';
GO
