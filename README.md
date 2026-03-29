# 🧬 Biotech Catalyst Trading Strategy

End-to-end Python pipeline for an event-driven trading strategy using ClinicalTrials.gov and market data APIs to capture pre-catalyst momentum in small-cap biotech stocks

## 📈 Overview

This project builds a trading strategy that:
1. identifies upcoming biotech catalyst events (clinical trial readouts)
2. scores company pipelines based on trial progression
3. simulates trades to capture momentum before clinical trial outcomes

This project explores the following idea:
Biotech stocks typically experience speculative price increases before the results of major clinical trials. Capturing this momentum is useful because it avoids the binary outcome of the clinical trials.

## 🤝 Strategy Logic

- **Clinical Trial Catalysts** are identified using primary completion dates from ClinicalTrials.gov
- Companies are scored using a **phase-weighted pipeline strength model**
- Positions are entered **28 days before catalyst events** and exited **1 day before the event** (in order to avoid the effect of the binary outcome)
- Filters are applied based on pipeline strength

## 💻 Tech Stack
- **Python**
- **Pandas / NumPy**
- **yfinance API** - historical price data
- **ClinicalTrials.gov API (pytrials)** - clinical trial data
- **Pathlib**

## 🏛️ Project Structure

biotech-catalyst-strategy/
│
├── src/
│   ├── trials.py      # extracts + processes clinical trial data
│   ├── prices.py      # downloads and aligns historical price data
│   ├── signals.py     # generates trades (entry/exit)
│   ├── metrics.py     # evaluates backtest with performance metrics
│   └── analysis.py    # optional deeper analysis (still in progress)
│
├── data/
│   ├── raw/
│   └── processed/
│
├── .gitignore
├── README.md


---

##  👩‍💻 Data Pipeline

1. Extracts clinical trial data from ClinicalTrials.gov  
2. Clean and structure trial phases, statuses, and dates  
3. Compute pipeline strength scores  
4. Extract catalyst events (primary completion dates)  
5. Download historical stock price data  
6. Generate trades based on entry/exit rules  

---

## 📊 Backtest Results

- Total Trades: 150+
- Win Rate: ~ 46%
- Average Return: ~ 1.6%
- Sharpe Ratio: ~ 0.8
- Max Drawdown: high (high tail risk)

---

## 👀 Key Insights

- Evidence of pre-catalyst momentum in biotech equities
- Positive average returns, but caused by a small number of large winners
- Strategy exhibits significant downside tail risk
- Indicates need for stronger risk management

---

## 🛑 Limitations

- Uses primary completion dates as proxies
- No transaction costs included
- Limited stock universe

---

## 🔨 Future Improvements

- Add position sizing & risk management
- Expand ticker universe
- Explore more robust pipeline scoring methods

---

## 🙋‍♀️ Author

Created by Aishi Dev