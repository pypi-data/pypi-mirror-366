import asyncio
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp_stock_analysis")

# Data class for clarity
class Holding:
    def __init__(self, symbol: str, qty: float, avg_cost: float):
        self.symbol = symbol
        self.qty = qty
        self.avg_cost = avg_cost

@mcp.tool()
async def fetch_market_data(symbol: str) -> Dict[str, Any]:
    """
    Fetch detailed market data for a given symbol:
    - Adjusted OHLCV history (1y)
    - Dividend & split history
    - Company fundamentals
    - Analyst recommendations
    - Insider transactions
    """
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1y", auto_adjust=True)
    info = ticker.info or {}
    dividends = ticker.dividends.to_dict()
    splits = ticker.splits.to_dict()
    try:
        rec = ticker.recommendations.to_dict()
    except:
        rec = {}
    try:
        insiders = ticker.get_insider_transactions().to_dict()
    except:
        insiders = {}
    return {
        "symbol": symbol,
        "history": hist.reset_index().to_dict(orient="list"),
        "info": info,
        "dividends": dividends,
        "splits": splits,
        "recommendations": rec,
        "insiders": insiders
    }

@mcp.tool()
async def fetch_market_data_multiple_tickers_parallel(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch market data in parallel for multiple ticker symbols.
    Each result contains:
    - OHLCV (1y)
    - Dividends and splits
    - Company info
    - Analyst recommendations
    - Insider transactions
    """
    async def safe_fetch(symbol):
        try:
            return await fetch_market_data(symbol)
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    tasks = [safe_fetch(sym) for sym in symbols]
    return await asyncio.gather(*tasks)

@mcp.tool()
async def analyze_stock(data: Dict[str, Any], qty: float, avg_cost: float) -> Dict[str, Any]:
    """
    Analyze a single stock:
    - Invested amount, PnL, IRR
    - Volatility, drawdown
    - RSI, MA50, MA200
    """
    hist = pd.DataFrame(data["history"])
    invested = qty * avg_cost
    price_now = data["info"].get("currentPrice", hist['Close'].iloc[-1])
    current_value = price_now * qty
    pnl = current_value - invested
    
    returns = hist['Close'].pct_change().dropna()
    vol = returns.std() * np.sqrt(252)
    cum = (1 + returns).cumprod()
    drawdown = (cum / cum.cummax() - 1).min()

    delta = hist['Close'].diff()
    up, down = delta.clip(lower=0), -delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    ma50 = hist['Close'].rolling(50).mean().iloc[-1]
    ma200 = hist['Close'].rolling(200).mean().iloc[-1]

    return {
        "symbol": data["symbol"],
        "qty": qty,
        "avg_cost": avg_cost,
        "invested": invested,
        "current_value": current_value,
        "pnl": pnl,
        "annual_volatility": vol,
        "max_drawdown": drawdown,
        "rsi": float(rsi),
        "ma50": float(ma50),
        "ma200": float(ma200)
    }

@mcp.tool()
async def analyze_multiple_stocks_parallel(stock_inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple stocks in parallel. Each input should be a dictionary with:
    - data: dict from fetch_market_data
    - qty: number of shares held
    - avg_cost: average cost per share

    Returns a list of computed metrics per stock.
    """
    async def analyze_wrapper(stock):
        return await analyze_stock(stock["data"], stock["qty"], stock["avg_cost"])

    tasks = [analyze_wrapper(s) for s in stock_inputs]
    return await asyncio.gather(*tasks)

@mcp.tool()
async def summarize_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Scrape recent Yahoo Finance headlines for a symbol.
    Returns top 5 with titles and timestamps.
    """
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []
    for item in soup.select('li.js-stream-content'):
        a = item.find('a')
        time = item.find('time')
        if a and time:
            articles.append({"title": a.get_text(strip=True), "datetime": time.get("datetime")})
    return {"symbol": symbol, "recent_news": articles[:5]}

@mcp.tool()
async def aggregate_portfolio(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarize entire portfolio:
    - total invested, value, return %
    - concentration >10%, weighted volatility
    """
    invested = sum(a['invested'] for a in analyses)
    current_value = sum(a['current_value'] for a in analyses)
    total_pnl = current_value - invested
    weights = {a['symbol']: a['current_value'] / current_value for a in analyses}
    concentration = [s for s, w in weights.items() if w > 0.1]
    port_vol = np.sqrt(sum((a['annual_volatility'] * weights[a['symbol']])**2 for a in analyses))
    return {
        "total_invested": invested,
        "current_value": current_value,
        "total_pnl": total_pnl,
        "return_pct": total_pnl / invested * 100,
        "weights": weights,
        "concentration": concentration,
        "portfolio_volatility": port_vol
    }

@mcp.tool()
async def generate_recommendations(summary: Dict[str, Any], analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate suggestions from portfolio summary:
    - overweight warnings
    - RSI-based notes
    - rebalance alerts
    """
    recs = []
    for a in analyses:
        w = summary["weights"][a['symbol']]
        if w > 0.2:
            recs.append({"symbol": a['symbol'], "note": "Overweight – consider trimming"})
        if a['rsi'] > 70:
            recs.append({"symbol": a['symbol'], "note": "Overbought RSI >70 – caution"})
    if summary["concentration"]:
        recs.append({"note": f"High concentration: {summary['concentration']}"})
    return {"recommendations": recs}

@mcp.tool()
async def render_report(analyses: List[Dict[str, Any]], summary: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
    """
    Create Markdown summary of portfolio:
    - overall stats, holding metrics, news and advice
    """
    md = "# Portfolio Analysis\n\n"
    md += f"- Total Invested: ₹{summary['total_invested']:.2f}\n"
    md += f"- Current Value: ₹{summary['current_value']:.2f}\n"
    md += f"- Return %: {summary['return_pct']:.2f}%\n\n"
    md += "## Holdings\n\n"
    md += "|Symbol|Qty|P&L|Volatility|RSI|Weight|\n"
    md += "|---|---|---|---|---|---|\n"
    for a in analyses:
        w = summary['weights'][a['symbol']]*100
        md += f"|{a['symbol']}|{a['qty']}|₹{a['pnl']:.2f}|{a['annual_volatility']:.2%}|{a['rsi']:.1f}|{w:.1f}%|\n"
    md += "\n## Recommendations\n"
    for r in recommendations["recommendations"]:
        sym = r.get("symbol", "")
        md += f"- {sym}: {r['note']}\n"
    md += "\n## Recent News Highlights\n"
    for a in analyses:
        md += f"### {a['symbol']}\n"
        news = a.get('recent_news', [])
        for n in news:
            md += f"- {n['datetime']}: {n['title']}\n"
    return md

if __name__ == "__main__":
    mcp.run(transport="stdio")
