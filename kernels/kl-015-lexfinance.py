```python
import os

def fetch_financial_data(ticker: str) -> dict:
    # Placeholder function to fetch financial data using an external API
    return {
        "ticker": ticker,
        "price": 150.75,
        "volume": 2345678,
        "change": -2.5,
        "change_percent": "-1.67%",
    }

if __name__ == "__main__":
    stock_ticker = input("Enter stock ticker: ")
    data = fetch_financial_data(stock_ticker)
    print(data)
```