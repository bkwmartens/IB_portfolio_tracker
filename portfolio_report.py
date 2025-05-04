import os
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ib_insync import IB
import yfinance as yf
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('.') / '.env')

MAPPING_FILE = "yf_symbols.json"

def refresh_symbol_mapping():
    ib = IB()
    ib.connect("127.0.0.1", 7497, clientId=2)
    portfolio = ib.portfolio()
    ib.disconnect()

    symbols = sorted(set(p.contract.symbol for p in portfolio))
    print("🔄 Refreshing YF symbol mapping...")

    mapping = {}
    for symbol in symbols:
        trial_symbols = [
            symbol,
            f"{symbol}.AS", f"{symbol}.PA", f"{symbol}.MI",
            f"{symbol}.F", f"{symbol}.AX", f"{symbol}.HK", f"{symbol}.TO"
        ]
        for yf_symbol in trial_symbols:
            try:
                ticker = yf.Ticker(yf_symbol)
                hist = ticker.history(period="2d")
                if not hist.empty and len(hist) >= 2:
                    mapping[symbol] = yf_symbol
                    print(f"✅ {symbol} → {yf_symbol}")
                    break
            except:
                continue
        if symbol not in mapping:
            print(f"❌ Could not resolve {symbol}")

    with open(MAPPING_FILE, "w") as f:
        json.dump(mapping, f, indent=2)
    print("✅ Saved YF mapping to", MAPPING_FILE)
    return mapping

# Load environment variables
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Connect to IB
ib = IB()
ib.connect("127.0.0.1", 7497, clientId=1)
portfolio = ib.portfolio()
ib.disconnect()

# Ensure mapping file exists and is up to date
if not os.path.exists(MAPPING_FILE):
    YF_SYMBOLS = refresh_symbol_mapping()
else:
    with open(MAPPING_FILE) as f:
        YF_SYMBOLS = json.load(f)
    ib_symbols = {p.contract.symbol for p in portfolio}
    if ib_symbols != set(YF_SYMBOLS.keys()):
        print("⚠️ YF mapping out of sync with portfolio. Updating...")
        YF_SYMBOLS = refresh_symbol_mapping()

# Fetch data and compute P&L
rows = []
total_daily_pnl = 0
total_unrealized = 0

for p in portfolio:
    symbol = p.contract.symbol
    yf_symbol = YF_SYMBOLS.get(symbol)

    if not yf_symbol:
        print(f"⚠️ No mapping for {symbol}")
        continue

    try:
        hist = yf.Ticker(yf_symbol).history(period="2d")
        if hist.empty or len(hist) < 2:
            print(f"⚠️ Not enough data for {symbol}")
            continue

        # ✅ Use iloc for future-proof indexing
        price_yesterday = hist['Close'].iloc[-2]
        price_today = hist['Close'].iloc[-1]
        daily_pnl = (price_today - price_yesterday) * p.position
        unrealized = (price_today - p.averageCost) * p.position

        rows.append({
            "symbol": symbol,
            "buy_price": round(p.averageCost, 2),
            "price_1d": round(price_yesterday, 2),
            "price_now": round(price_today, 2),
            "qty": p.position,
            "daily_pnl": round(daily_pnl, 2),
            "unrealized": round(unrealized, 2)
        })

        total_daily_pnl += daily_pnl
        total_unrealized += unrealized

    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")

# Create HTML table
html_table = """
<table border="1" cellpadding="5" cellspacing="0">
<tr>
<th>Symbol</th><th>Buy Price</th><th>Price 1d Ago</th><th>Price Now</th><th>Qty</th><th>Daily P&L</th><th>Unrealized P&L</th>
</tr>
"""
for row in rows:
    html_table += f"""
<tr>
<td>{row['symbol']}</td><td>{row['buy_price']}</td><td>{row['price_1d']}</td><td>{row['price_now']}</td>
<td>{row['qty']}</td><td>{row['daily_pnl']}</td><td>{row['unrealized']}</td>
</tr>
"""
html_table += "</table>"

# Prepare email
msg = MIMEMultipart("alternative")
date_str = datetime.today().strftime("%Y-%m-%d")
subject = f"{date_str} | Daily P&L: {round(total_daily_pnl,2)} | Unrealized: {round(total_unrealized,2)}"
msg["Subject"] = subject
msg["From"] = EMAIL_ADDRESS
msg["To"] = EMAIL_TO

html_body = f"""
<h2>📈 Daily Portfolio Report - {date_str}</h2>
{html_table}
<p><strong>Total Daily P&L:</strong> {round(total_daily_pnl, 2)}</p>
<p><strong>Total Unrealized P&L:</strong> {round(total_unrealized, 2)}</p>
"""

msg.attach(MIMEText(html_body, "html"))

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    print("📬 Email sent.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")