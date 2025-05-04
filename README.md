💼 IB Daily Portfolio Email Report

Automatically fetch your Interactive Brokers portfolio, calculate daily and unrealized P&L, and receive a daily email report with a portfolio summary.

---

✨ Features

- Connects to **Interactive Brokers** via API (TWS or IB Gateway)
- Pulls live portfolio data and current market prices
- Retrieves historical prices from **Yahoo Finance**
- Calculates:
  - Buy price
  - Price 1 day ago
  - Current price
  - Daily P&L
  - Unrealized P&L
- Sends a daily email report via **Gmail SMTP**
- Easily automatable using **cron** on macOS/Linux

---

📦 Requirements

- Python 3.8+
- An Interactive Brokers account
- IB Gateway (or TWS) running and API enabled
- Gmail account with App Password

---

🚀 Setup Instructions

1. Clone the Repository

```bash
git clone https://github.com/yourusername/ib-daily-portfolio.git
cd portfolio_report
```

2. Set Up Conda Environment

```bash
conda create -n portfoliostocks python=3.11
conda activate portfoliostocks
pip install -r requirements.txt
```

Or use the `environment.yml`:

```bash
conda env create -f environment.yml
conda activate portfoliostocks
```

3. Create a `.env` File

Create a `.env` file in the root directory with the following:

```env
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
EMAIL_TO=recipient_email@gmail.com

IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
```

4. Enable API Access in IB Gateway or TWS

See below ⬇️ for detailed setup.

5. Run the Script

```bash
python portfolio_report.py
```

6. Automate with Cron (macOS)

Edit your crontab:

```bash
crontab -e
```

Add this line to run daily at 18:00:

```bash
0 18 * * * /Users/[yourusername]/miniconda3/envs/portfoliostocks/bin/python /[full_path_to]/portfolio_report.py
```

---

📧 Gmail Setup (App Passwords)

1. Enable 2-Step Verification on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate a password for "Mail" on "Mac"
4. Paste that into your `.env` file

---

🔐 Security

- Your `.env` contains secrets — never commit it!
- Add `.env` to `.gitignore`:

```gitignore
.env
```

---

📊 Example Email Output

```
Subject: Daily Portfolio Report - 2025-05-04 - Daily P&L: +$122.45
```

| Ticker | Buy Price | Price 1D Ago | Current Price | Daily P&L | Unrealized P&L |
|--------|-----------|--------------|----------------|-----------|----------------|
| AAPL   | $145.00   | $171.00      | $173.00        | +$2.00    | +$28.00        |
| TSLA   | $240.00   | $237.00      | $238.50        | +$1.50    | -$1.50         |

---

🤖 Using IB Gateway (or TWS) with API

Interactive Brokers offers two apps that enable API access:

Option 1: IB Gateway (Preferred for Headless/Automated Use)

1. Download IB Gateway:  
   https://www.interactivebrokers.com/en/index.php?f=16457

2. Log in with your **IBKR credentials**

3. Enable API:
   - Go to **Configure > API > Settings**
   - ✅ Check **"Enable ActiveX and Socket Clients"**
   - ✅ Enable **"Download open orders on connection"**
   - Port: `7497` (TWS) or `4002` (Gateway Live) or `4001` (Gateway Paper)
   - Add `127.0.0.1` to **Trusted IPs**

4. Leave the Gateway running — your script connects to it.

Option 2: Trader Workstation (TWS)

Same as above, but less ideal for automated environments (TWS is a full GUI app).

---

📄 License

MIT

---

🙋 Questions?

Open an issue or reach out!
