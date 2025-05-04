import json
from ib_insync import IB
import yfinance as yf

SAVE_PATH = "yf_symbols.json"

ib = IB()
ib.connect("127.0.0.1", 7497, clientId=2)

portfolio = ib.portfolio()
symbols = sorted(set(p.contract.symbol for p in portfolio))

print("🔎 Attempting Yahoo Finance mapping...\n")

mapping = {}
for symbol in symbols:
    trial_symbols = [
        symbol,
        f"{symbol}.AS",   # Euronext Amsterdam
        f"{symbol}.PA",   # Paris
        f"{symbol}.MI",   # Milan
        f"{symbol}.F",    # Frankfurt
        f"{symbol}.AX",   # Australia
        f"{symbol}.HK",   # Hong Kong
        f"{symbol}.TO",   # Toronto
    ]
    
    matched = False
    for yf_symbol in trial_symbols:
        try:
            yf_ticker = yf.Ticker(yf_symbol)
            hist = yf_ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                mapping[symbol] = yf_symbol
                print(f"✅ {symbol} → {yf_symbol}")
                matched = True
                break
        except Exception:
            continue

    if not matched:
        print(f"❌ No match found for {symbol}")

ib.disconnect()

# Save to JSON file
with open(SAVE_PATH, "w") as f:
    json.dump(mapping, f, indent=2)

print(f"\n📁 Saved mapping to '{SAVE_PATH}'")