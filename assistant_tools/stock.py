import yfinance as yf

def get_stock_price(symbol: str) -> float:
    """
    Fetches the latest closing stock price for a given symbol.
    """
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price
