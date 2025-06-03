# app/data.py

# For simplicity, I'll just copy one stock. You'd convert your JS dummyData.js to this Python dict format.
# Make sure all keys are strings and values are appropriate Python types.
# In a real scenario, this would come from a database.

# app/data.py

dummy_stock_data_py = {
  "COALINDIA": {
    "id": "COALINDIA",
    "name": "Coal India Ltd.",
    "symbol": "COALINDIA",
    "bseCode": "533278",
    "nseCode": "COALINDIA",
    "sector": "Mining & Minerals",
    "industry": "Coal",
    "currentPrice": 450.75,
    "previousClose": 448.5,
    "dayHigh": 455.2,
    "dayLow": 448.5,
    "yearHigh": 480.0,
    "yearLow": 220.0,
    "marketCapRaw": 278000,  # This was 'marketCap' in JS, mapping to 'marketCapRaw'
    "outstandingShares": 616.27,
    "dividendPerShare": 24.25,
    "faceValue": 10,
    "bookValuePerShare": 150.3,
    "earningsPerShareTTM": 45.8,
    "netProfitAnnualRaw": 28125,  # This was 'netProfitAnnual' in JS
    "salesAnnualRaw": 139500,  # This was 'salesAnnual' in JS
    "shareholderEquityRaw": 92600,  # This was 'shareholderEquity' in JS
    "earningsBeforeInterestAndTaxAnnualRaw": 38000,  # This was 'earningsBeforeInterestAndTaxAnnual' in JS
    "capitalEmployedAnnualRaw": 120000,  # This was 'capitalEmployedAnnual' in JS
    "priceHistory": [
      {"date": "2023-05-01", "close": 230, "volume": 500000},
      {"date": "2023-05-15", "close": 235, "volume": 600000},
      {"date": "2023-06-01", "close": 240, "volume": 550000},
      {"date": "2023-06-15", "close": 238, "volume": 520000},
      {"date": "2023-07-01", "close": 250, "volume": 700000},
      {"date": "2023-07-15", "close": 260, "volume": 750000},
      {"date": "2023-08-01", "close": 280, "volume": 800000},
      {"date": "2023-08-15", "close": 275, "volume": 780000},
      {"date": "2023-09-01", "close": 300, "volume": 900000},
      {"date": "2023-09-15", "close": 310, "volume": 950000},
      {"date": "2023-10-01", "close": 320, "volume": 850000},
      {"date": "2023-10-15", "close": 315, "volume": 820000},
      {"date": "2023-11-01", "close": 350, "volume": 1000000},
      {"date": "2023-11-15", "close": 360, "volume": 1100000},
      {"date": "2023-12-01", "close": 380, "volume": 1200000},
      {"date": "2023-12-15", "close": 370, "volume": 1000000},
      {"date": "2024-01-01", "close": 400, "volume": 1300000},
      {"date": "2024-01-15", "close": 410, "volume": 1350000},
      {"date": "2024-02-01", "close": 430, "volume": 1400000},
      {"date": "2024-02-15", "close": 425, "volume": 1300000},
      {"date": "2024-03-01", "close": 440, "volume": 1500000},
      {"date": "2024-03-15", "close": 450, "volume": 1600000},
      {"date": "2024-04-01", "close": 460, "volume": 1400000},
      {"date": "2024-04-15", "close": 455, "volume": 1350000},
      {"date": "2024-05-01", "close": 445, "volume": 1200000},
      {"date": "2024-05-14", "close": 450.75, "volume": 1250000},
    ],
    "pros": [
      "Company is almost debt free.",
      "Company is expected to give good quarter.",
      "Company has good return on equity (ROE) track record: 3 Years ROE 35.0%",
      "Company has been maintaining a healthy dividend payout of 50.0%",
    ],
    "cons": [
      "The company has delivered a poor sales growth of 8.33% over past five years.",
      "Promoter holding has decreased over last quarter: -2.50%",
    ],
    "about": "Coal India Limited (CIL) is an Indian public sector undertaking, engaged in coal mining and refining. It is the largest coal-producing company in the world and a Maharatna public sector undertaking. The company contributes to around 82% of the coal production in India. The major consumers of the company are power and steel sectors. Consumers from other sectors include cement, fertilizers, brick kilns etc.",
    "keyPoints": [
      "A Maharatna company.",
      "Coal India was incorporated in 1973 as Coal Mines Authority Ltd. after the nationalization of the coal sector.",
    ],
    "peerComparison": [
      {"id": "NLCINDIA", "name": "NLC India", "cmp": 230.5, "pe": 15.5, "marketCap": 32000, "dividendYield": 2.5, "netProfitQtr": 500, "qtrProfitVar": 10.2, "salesQtr": 3500, "qtrSalesVar": 5.1, "roce": 12.0,},
      {"id": "SINGARENI", "name": "Singareni Collieries", "cmp": "N/A", "pe": "N/A", "marketCap": "N/A (Unlisted)", "dividendYield": "N/A", "netProfitQtr": 450, "qtrProfitVar": 8.0, "salesQtr": 3200, "qtrSalesVar": 4.5, "roce": "N/A",},
      {"id": "VEDL", "name": "Vedanta", "cmp": 434.7, "pe": 12.21, "marketCap": 169864.64, "dividendYield": 6.38, "netProfitQtr": 560.53, "qtrProfitVar": 12.45, "salesQtr": 37634.54, "qtrSalesVar": -1.02, "roce": 40.04,},
    ],
    "quarterlyResults": [
      {"quarter": "Mar 2023", "sales": 35161, "expenses": 25214, "operatingProfit": 9947, "opm": 28, "otherIncome": 1200, "interest": 150, "depreciation": 1100, "profitBeforeTax": 9897, "tax": 25, "netProfit": 6500, "eps": 10.55,},
      {"quarter": "Jun 2023", "sales": 32000, "expenses": 23000, "operatingProfit": 9000, "opm": 28, "otherIncome": 1100, "interest": 140, "depreciation": 1050, "profitBeforeTax": 8910, "tax": 24, "netProfit": 6000, "eps": 9.74,},
      {"quarter": "Sep 2023", "sales": 33500, "expenses": 24500, "operatingProfit": 9000, "opm": 27, "otherIncome": 1150, "interest": 130, "depreciation": 1080, "profitBeforeTax": 9000, "tax": 25, "netProfit": 6200, "eps": 10.06,},
      {"quarter": "Dec 2023", "sales": 36000, "expenses": 26000, "operatingProfit": 10000, "opm": 28, "otherIncome": 1250, "interest": 120, "depreciation": 1120, "profitBeforeTax": 10010, "tax": 26, "netProfit": 7000, "eps": 11.36,},
      {"quarter": "Mar 2024", "sales": 38000, "expenses": 27000, "operatingProfit": 11000, "opm": 29, "otherIncome": 1300, "interest": 110, "depreciation": 1150, "profitBeforeTax": 11040, "tax": 27, "netProfit": 7500, "eps": 12.17,},
    ],
    "profitAndLoss": [
      {"year": "Mar 2021", "sales": 90000, "expenses": 70000, "operatingProfit": 20000, "opm": 22, "otherIncome": 4000, "interest": 800, "depreciation": 4000, "profitBeforeTax": 19200, "tax": 25, "netProfit": 12000, "eps": 19.47,},
      {"year": "Mar 2022", "sales": 105000, "expenses": 80000, "operatingProfit": 25000, "opm": 24, "otherIncome": 4500, "interest": 700, "depreciation": 4200, "profitBeforeTax": 24600, "tax": 25, "netProfit": 17000, "eps": 27.58,},
      {"year": "Mar 2023", "sales": 125000, "expenses": 95000, "operatingProfit": 30000, "opm": 24, "otherIncome": 5000, "interest": 600, "depreciation": 4500, "profitBeforeTax": 29900, "tax": 25, "netProfit": 22000, "eps": 35.7,},
      {"year": "TTM", "sales": 139500, "expenses": 105000, "operatingProfit": 34500, "opm": 25, "otherIncome": 5200, "interest": 500, "depreciation": 4600, "profitBeforeTax": 34600, "tax": 25, "netProfit": 28125, "eps": 45.8,},
    ],
    "balanceSheet": [ # Updated to match JS structure
      {"item": "Share Capital", "value": 6163, "date": "Mar 2023"},
      {"item": "Reserves", "value": 86437, "date": "Mar 2023"},
      {"item": "Borrowings", "value": 5000, "date": "Mar 2023"},
      # Add other balance sheet items if present in your full JS data
      # For example:
      # {"item": "Total Liabilities", "value": 150000, "date": "Mar 2023"},
      # {"item": "Fixed Assets", "value": 70000, "date": "Mar 2023"},
      # {"item": "Current Assets", "value": 80000, "date": "Mar 2023"},
      # {"item": "Total Assets", "value": 150000, "date": "Mar 2023"},
    ],
    "cashFlows": [
      {"year": "Mar 2021", "cashFromOperating": 18000, "cashFromInvesting": -4000, "cashFromFinancing": -9000, "netCashFlow": 5000,},
      {"year": "Mar 2022", "cashFromOperating": 19000, "cashFromInvesting": -4500, "cashFromFinancing": -9500, "netCashFlow": 5000,},
      {"year": "Mar 2023", "cashFromOperating": 20000, "cashFromInvesting": -5000, "cashFromFinancing": -10000, "netCashFlow": 5000,},
      {"year": "TTM", "cashFromOperating": 22000, "cashFromInvesting": -5500, "cashFromFinancing": -11000, "netCashFlow": 5500,},
    ],
    "shareholdingPatternHistory": [
      {"date": "Jun 2022", "promoters": 63.5, "fii": 18.16, "dii": 10.2, "public": 8.14, "others": 0.0,},
      {"date": "Sep 2022", "promoters": 63.3, "fii": 20.32, "dii": 10.5, "public": 7.88, "others": 0.0,},
      {"date": "Dec 2022", "promoters": 63.13, "fii": 21.8, "dii": 11.05, "public": 7.52, "others": 0.0,},
      {"date": "Mar 2023", "promoters": 63.13, "fii": 22.1, "dii": 11.5, "public": 7.27, "others": 0.0,},
      {"date": "Jun 2023", "promoters": 63.13, "fii": 22.5, "dii": 12.0, "public": 7.37, "others": 0.0,},
    ],
  },
  "RELIANCE": { # Minimal RELIANCE data for list view and basic details
    "id": "RELIANCE",
    "name": "Reliance Industries Ltd.",
    "symbol": "RELIANCE",
    "bseCode": "500325",
    "nseCode": "RELIANCE",
    "sector": "Diversified",
    "industry": "Conglomerates",
    "currentPrice": 2900.50,
    "previousClose": 2880.00,
    "dayHigh": 2915.00,
    "dayLow": 2890.00,
    "yearHigh": 3024.90,
    "yearLow": 2012.15,
    "marketCapRaw": 1950000,
    "outstandingShares": 676.6,
    "dividendPerShare": 9.00,
    "faceValue": 10,
    "bookValuePerShare": 1400.75,
    "earningsPerShareTTM": 100.50,
    "netProfitAnnualRaw": 67000,
    "salesAnnualRaw": 850000,
    "shareholderEquityRaw": 948000,
    "earningsBeforeInterestAndTaxAnnualRaw": 120000,
    "capitalEmployedAnnualRaw": 1500000,
    "priceHistory": [{"date": "2024-05-14", "close": 2900.50, "volume": 1000000}], # Very minimal
    "pros": ["Strong growth in retail and telecom.", "Diversified business."],
    "cons": ["High debt levels.", "Complex holding structure."],
    "about": "Reliance Industries Limited is an Indian multinational conglomerate company...",
    "keyPoints": ["Largest publicly traded company in India by market capitalisation."],
    "peerComparison": [], # Add peers if needed
    "quarterlyResults": [], # Add quarterly results if needed
    "profitAndLoss": [], # Add P&L if needed
    "cashFlows": [], # Add cash flows if needed
    "shareholdingPatternHistory": [], # Add shareholding if needed
    "balanceSheet": [], # Add balance sheet if needed
  }
}

all_stocks_summary_py = [
    {
        "id": "COALINDIA", # Matches key in dummy_stock_data_py
        # name, symbol will be fetched from dummy_stock_data_py by the API endpoint
    },
    {
        "id": "RELIANCE", # Matches key in dummy_stock_data_py
    }
]