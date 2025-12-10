-- Sample data for Financial Insights Database
-- Realistic financial data for testing and development

USE financial_insights_db;
GO

-- Insert sample portfolios
INSERT INTO dbo.portfolios (name, strategy, risk_profile, inception_date, initial_capital, current_value, owner_name, description)
VALUES
    ('Growth Portfolio', 'growth', 'aggressive', '2023-01-15', 100000.00, 125000.00, 'John Smith', 'Tech-focused growth portfolio with high risk tolerance'),
    ('Balanced Fund', 'balanced', 'moderate', '2022-06-01', 250000.00, 275000.00, 'Jane Doe', 'Balanced mix of stocks and bonds for steady growth'),
    ('Income Portfolio', 'income', 'conservative', '2021-09-15', 500000.00, 535000.00, 'Robert Johnson', 'Dividend-focused portfolio for stable income'),
    ('Tech Momentum', 'momentum', 'aggressive', '2023-05-01', 150000.00, 162000.00, 'Sarah Williams', 'Technology sector momentum strategy');
GO

-- Insert sample holdings
INSERT INTO dbo.holdings (portfolio_id, symbol, asset_type, quantity, purchase_date, purchase_price, current_price, sector, country)
VALUES
    -- Growth Portfolio (ID: 1)
    (1, 'AAPL', 'stock', 250.00, '2023-01-20', 135.50, 185.92, 'Technology', 'USA'),
    (1, 'MSFT', 'stock', 200.00, '2023-02-10', 245.30, 378.85, 'Technology', 'USA'),
    (1, 'NVDA', 'stock', 150.00, '2023-03-15', 265.00, 495.22, 'Technology', 'USA'),
    (1, 'GOOGL', 'stock', 180.00, '2023-04-01', 105.00, 139.70, 'Technology', 'USA'),
    (1, 'TSLA', 'stock', 100.00, '2023-02-25', 205.00, 242.84, 'Automotive', 'USA'),

    -- Balanced Fund (ID: 2)
    (2, 'SPY', 'etf', 300.00, '2022-06-15', 385.00, 455.48, 'Diversified', 'USA'),
    (2, 'AGG', 'etf', 500.00, '2022-07-01', 105.00, 98.75, 'Fixed Income', 'USA'),
    (2, 'VTI', 'etf', 400.00, '2022-08-10', 195.00, 245.30, 'Diversified', 'USA'),
    (2, 'JNJ', 'stock', 150.00, '2022-09-05', 165.00, 156.35, 'Healthcare', 'USA'),
    (2, 'PG', 'stock', 200.00, '2022-10-12', 135.00, 152.44, 'Consumer Goods', 'USA'),

    -- Income Portfolio (ID: 3)
    (3, 'VZ', 'stock', 800.00, '2021-09-20', 52.50, 41.15, 'Telecommunications', 'USA'),
    (3, 'T', 'stock', 1000.00, '2021-10-15', 25.50, 22.34, 'Telecommunications', 'USA'),
    (3, 'XOM', 'stock', 600.00, '2021-11-01', 58.00, 108.54, 'Energy', 'USA'),
    (3, 'CVX', 'stock', 500.00, '2021-12-10', 115.00, 155.85, 'Energy', 'USA'),
    (3, 'MO', 'stock', 700.00, '2022-01-15', 47.00, 51.20, 'Consumer Goods', 'USA'),
    (3, 'SCHD', 'etf', 1500.00, '2022-02-01', 72.00, 78.55, 'Dividend ETF', 'USA'),

    -- Tech Momentum (ID: 4)
    (4, 'META', 'stock', 150.00, '2023-05-10', 240.00, 511.80, 'Technology', 'USA'),
    (4, 'AMZN', 'stock', 400.00, '2023-05-15', 110.00, 181.05, 'Technology', 'USA'),
    (4, 'AMD', 'stock', 300.00, '2023-06-01', 110.00, 135.24, 'Technology', 'USA'),
    (4, 'CRM', 'stock', 100.00, '2023-06-10', 205.00, 282.45, 'Technology', 'USA');
GO

-- Insert sample transactions
INSERT INTO dbo.transactions (portfolio_id, symbol, transaction_type, quantity, price, transaction_date, fees, notes)
VALUES
    -- Growth Portfolio transactions
    (1, 'AAPL', 'buy', 250.00, 135.50, '2023-01-20', 10.00, 'Initial purchase'),
    (1, 'MSFT', 'buy', 200.00, 245.30, '2023-02-10', 10.00, 'Initial purchase'),
    (1, 'NVDA', 'buy', 150.00, 265.00, '2023-03-15', 10.00, 'AI boom investment'),
    (1, 'GOOGL', 'buy', 180.00, 105.00, '2023-04-01', 10.00, 'After stock split'),
    (1, 'TSLA', 'buy', 100.00, 205.00, '2023-02-25', 10.00, 'EV growth play'),
    (1, 'AAPL', 'dividend', 0.24, 185.00, '2024-02-15', 0.00, 'Quarterly dividend'),
    (1, 'MSFT', 'dividend', 0.68, 370.00, '2024-05-15', 0.00, 'Quarterly dividend'),

    -- Balanced Fund transactions
    (2, 'SPY', 'buy', 300.00, 385.00, '2022-06-15', 15.00, 'Core position'),
    (2, 'AGG', 'buy', 500.00, 105.00, '2022-07-01', 12.00, 'Bond allocation'),
    (2, 'VTI', 'buy', 400.00, 195.00, '2022-08-10', 15.00, 'Total market exposure'),
    (2, 'JNJ', 'buy', 150.00, 165.00, '2022-09-05', 8.00, 'Healthcare defensive'),
    (2, 'PG', 'buy', 200.00, 135.00, '2022-10-12', 8.00, 'Consumer staples'),
    (2, 'SPY', 'dividend', 1.48, 450.00, '2024-03-20', 0.00, 'Quarterly distribution'),
    (2, 'JNJ', 'dividend', 1.13, 160.00, '2024-06-05', 0.00, 'Quarterly dividend'),

    -- Income Portfolio transactions
    (3, 'VZ', 'buy', 800.00, 52.50, '2021-09-20', 20.00, 'High dividend yield'),
    (3, 'T', 'buy', 1000.00, 25.50, '2021-10-15', 15.00, 'Telecom dividend'),
    (3, 'XOM', 'buy', 600.00, 58.00, '2021-11-01', 18.00, 'Energy sector'),
    (3, 'CVX', 'buy', 500.00, 115.00, '2021-12-10', 20.00, 'Energy diversification'),
    (3, 'MO', 'buy', 700.00, 47.00, '2022-01-15', 15.00, 'High yield stock'),
    (3, 'SCHD', 'buy', 1500.00, 72.00, '2022-02-01', 25.00, 'Dividend ETF core'),
    (3, 'VZ', 'dividend', 0.6525, 42.00, '2024-02-01', 0.00, 'Quarterly dividend'),
    (3, 'T', 'dividend', 0.2775, 23.00, '2024-03-01', 0.00, 'Quarterly dividend'),
    (3, 'XOM', 'dividend', 0.91, 105.00, '2024-03-15', 0.00, 'Quarterly dividend'),

    -- Tech Momentum transactions
    (4, 'META', 'buy', 150.00, 240.00, '2023-05-10', 10.00, 'AI narrative'),
    (4, 'AMZN', 'buy', 400.00, 110.00, '2023-05-15', 15.00, 'Cloud growth'),
    (4, 'AMD', 'buy', 300.00, 110.00, '2023-06-01', 12.00, 'AI chips'),
    (4, 'CRM', 'buy', 100.00, 205.00, '2023-06-10', 8.00, 'Enterprise software');
GO

-- Insert sample price data (last 30 days for key symbols)
DECLARE @EndDate DATE = GETDATE();
DECLARE @StartDate DATE = DATEADD(DAY, -30, @EndDate);
DECLARE @CurrentDate DATE = @StartDate;

-- AAPL prices
WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dbo.prices (symbol, price_date, open_price, high_price, low_price, close_price, volume, adjusted_close, daily_return)
    VALUES (
        'AAPL',
        @CurrentDate,
        185.00 + (RAND(CHECKSUM(NEWID())) * 5 - 2.5),
        187.00 + (RAND(CHECKSUM(NEWID())) * 5 - 2.5),
        183.00 + (RAND(CHECKSUM(NEWID())) * 5 - 2.5),
        185.92 + (RAND(CHECKSUM(NEWID())) * 5 - 2.5),
        75000000 + (RAND(CHECKSUM(NEWID())) * 25000000),
        185.92 + (RAND(CHECKSUM(NEWID())) * 5 - 2.5),
        (RAND(CHECKSUM(NEWID())) * 4 - 2) / 100.0
    );

    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- MSFT prices
SET @CurrentDate = @StartDate;
WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dbo.prices (symbol, price_date, open_price, high_price, low_price, close_price, volume, adjusted_close, daily_return)
    VALUES (
        'MSFT',
        @CurrentDate,
        376.00 + (RAND(CHECKSUM(NEWID())) * 8 - 4),
        380.00 + (RAND(CHECKSUM(NEWID())) * 8 - 4),
        374.00 + (RAND(CHECKSUM(NEWID())) * 8 - 4),
        378.85 + (RAND(CHECKSUM(NEWID())) * 8 - 4),
        25000000 + (RAND(CHECKSUM(NEWID())) * 10000000),
        378.85 + (RAND(CHECKSUM(NEWID())) * 8 - 4),
        (RAND(CHECKSUM(NEWID())) * 4 - 2) / 100.0
    );

    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- SPY prices (S&P 500 ETF)
SET @CurrentDate = @StartDate;
WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dbo.prices (symbol, price_date, open_price, high_price, low_price, close_price, volume, adjusted_close, daily_return)
    VALUES (
        'SPY',
        @CurrentDate,
        453.00 + (RAND(CHECKSUM(NEWID())) * 6 - 3),
        457.00 + (RAND(CHECKSUM(NEWID())) * 6 - 3),
        451.00 + (RAND(CHECKSUM(NEWID())) * 6 - 3),
        455.48 + (RAND(CHECKSUM(NEWID())) * 6 - 3),
        65000000 + (RAND(CHECKSUM(NEWID())) * 30000000),
        455.48 + (RAND(CHECKSUM(NEWID())) * 6 - 3),
        (RAND(CHECKSUM(NEWID())) * 3 - 1.5) / 100.0
    );

    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;
GO

-- Insert benchmark data (S&P 500, NASDAQ, Dow Jones)
DECLARE @EndDate DATE = GETDATE();
DECLARE @StartDate DATE = DATEADD(DAY, -30, @EndDate);
DECLARE @CurrentDate DATE = @StartDate;

-- S&P 500
WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dbo.benchmarks (index_name, price_date, index_value, daily_return, volume)
    VALUES (
        'S&P 500',
        @CurrentDate,
        4550.00 + (RAND(CHECKSUM(NEWID())) * 100 - 50),
        (RAND(CHECKSUM(NEWID())) * 3 - 1.5) / 100.0,
        3500000000 + (RAND(CHECKSUM(NEWID())) * 500000000)
    );

    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- NASDAQ Composite
SET @CurrentDate = @StartDate;
WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dbo.benchmarks (index_name, price_date, index_value, daily_return, volume)
    VALUES (
        'NASDAQ',
        @CurrentDate,
        14200.00 + (RAND(CHECKSUM(NEWID())) * 200 - 100),
        (RAND(CHECKSUM(NEWID())) * 4 - 2) / 100.0,
        4500000000 + (RAND(CHECKSUM(NEWID())) * 800000000)
    );

    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- Dow Jones Industrial Average
SET @CurrentDate = @StartDate;
WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dbo.benchmarks (index_name, price_date, index_value, daily_return, volume)
    VALUES (
        'DOW JONES',
        @CurrentDate,
        35500.00 + (RAND(CHECKSUM(NEWID())) * 300 - 150),
        (RAND(CHECKSUM(NEWID())) * 2.5 - 1.25) / 100.0,
        300000000 + (RAND(CHECKSUM(NEWID())) * 100000000)
    );

    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;
GO

-- Update current prices in holdings from latest price data
EXEC dbo.sp_update_holding_prices;
GO

-- Update portfolio current values
UPDATE p
SET current_value = total_holdings.total_value
FROM dbo.portfolios p
INNER JOIN (
    SELECT
        portfolio_id,
        SUM(current_value) AS total_value
    FROM dbo.holdings
    GROUP BY portfolio_id
) total_holdings ON p.portfolio_id = total_holdings.portfolio_id;
GO

PRINT 'Sample data inserted successfully!';
PRINT 'Portfolios: 4';
PRINT 'Holdings: 20 positions across 4 portfolios';
PRINT 'Transactions: 25+ historical transactions';
PRINT 'Prices: 30 days of historical data for key symbols';
PRINT 'Benchmarks: S&P 500, NASDAQ, Dow Jones indices';
GO
