# 📊 Retail Sales Analytics & Forecasting Dashboard

> Interactive multi-panel analytics dashboard covering 3 years of retail sales data across 5 regions, 5 categories, and 3 channels — with automated 90-day revenue forecasting.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-purple?logo=plotly)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-1.5+-green)](https://pandas.pydata.org)

---

## 🎯 What This Does

Transforms raw transactional sales data into an **interactive HTML dashboard** that answers the questions a business team actually asks:

- Which region/category/channel is driving (or dragging) revenue?
- What does revenue look like next quarter?
- Is average order value growing or declining?
- How does this year compare to last?

---

## 📸 Dashboard Panels

| Panel | Insight |
|---|---|
| Monthly Revenue + Forecast | Trend line with 3-month WMA forecast |
| Revenue by Region | Bar chart of regional contribution |
| Channel Mix | Pie chart — Online vs In-Store vs Wholesale |
| Category Heatmap | Revenue intensity by month × category |
| YoY Comparison | 2022 vs 2023 vs 2024 monthly revenue |
| Avg Revenue per Order | Order quality trend over time |
| Quarterly Breakdown | Seasonal patterns across all 12 quarters |

---

## 📈 Key Findings (on generated data)

- **Revenue grew 12% YoY** in 2023→2024, driven by the West region and Electronics
- **Q4 seasonal peak** is 28–32% above quarterly average — driven by year-end spend
- **Online channel** outperforms in-store by ~15% on average order value
- **Forecasted revenue** for Q1 2025 indicates continued growth of ~8–10%

---

## ⚙️ Setup & Run

```bash
git clone https://github.com/aaditya-bartwal/sales-analytics-dashboard.git
cd sales-analytics-dashboard
pip install -r requirements.txt
python sales_analytics.py
# Open outputs/sales_dashboard.html in your browser
```

---

## 🗂 Project Structure

```
project2_sales_analytics/
├── sales_analytics.py       # Full pipeline + dashboard builder
├── requirements.txt
├── outputs/
│   ├── retail_sales.csv     # Generated dataset (3 years, ~800k rows)
│   └── sales_dashboard.html # Interactive Plotly dashboard
└── README.md
```

---

## 🛠 Tech Stack

- **Pandas** — data wrangling and aggregation
- **Plotly** — interactive multi-panel dashboard
- **NumPy** — forecasting calculations
- Custom **Weighted Moving Average** forecasting with trend adjustment

---

*Built as part of M.Sc. Data Science — IU International University, Berlin*
