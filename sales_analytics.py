"""
Retail Sales Analytics & Forecasting Dashboard
===============================================
Generates a comprehensive multi-page HTML dashboard with:
  - Revenue & order trends
  - Regional & category performance
  - Month-over-month and YoY analysis
  - 90-day revenue forecast using weighted moving average
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os, warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_sales_data(seed=42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", "2024-12-31", freq="D")

    regions    = ["North", "South", "East", "West", "Central"]
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Food & Beverage"]
    channels   = ["Online", "In-Store", "Wholesale"]

    region_mult    = {"North": 1.15, "South": 0.90, "East": 1.05, "West": 1.20, "Central": 0.95}
    category_mult  = {"Electronics": 1.40, "Clothing": 1.00, "Home & Garden": 0.85,
                      "Sports": 0.95, "Food & Beverage": 0.75}
    channel_mult   = {"Online": 1.10, "In-Store": 0.95, "Wholesale": 0.85}

    records = []
    for date in dates:
        # Seasonal component (Q4 peak, Q1 trough)
        season = 1 + 0.30 * np.sin((date.dayofyear / 365) * 2 * np.pi - np.pi/2)
        # Year-over-year growth
        yoy = 1 + 0.12 * (date.year - 2022)
        # Weekday dip
        weekday_factor = 0.75 if date.weekday() >= 5 else 1.0

        n_orders = max(1, int(rng.normal(80 * season * yoy * weekday_factor, 15)))
        for _ in range(min(n_orders, 150)):
            region   = rng.choice(regions)
            category = rng.choice(categories)
            channel  = rng.choice(channels, p=[0.50, 0.35, 0.15])
            base_rev = rng.uniform(20, 500)
            revenue  = (base_rev
                        * region_mult[region]
                        * category_mult[category]
                        * channel_mult[channel]
                        * season * yoy
                        * rng.uniform(0.85, 1.15))
            qty      = rng.integers(1, 6)
            records.append({
                "Date":     date,
                "Region":   region,
                "Category": category,
                "Channel":  channel,
                "Revenue":  round(revenue * qty, 2),
                "Quantity": qty,
                "Orders":   1
            })

    df = pd.DataFrame(records)
    df["Month"]  = df["Date"].dt.to_period("M").astype(str)
    df["Year"]   = df["Date"].dt.year
    df["Quarter"] = df["Date"].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"})
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. FORECASTING — Weighted Moving Average + Trend
# ─────────────────────────────────────────────────────────────────────────────

def forecast_revenue(monthly_rev, periods=3):
    """Simple weighted moving average forecast with linear trend adjustment."""
    values = monthly_rev.values
    weights = np.array([1, 2, 3, 4, 5, 6])
    weights = weights / weights.sum()

    forecasts = []
    series = list(values)
    for _ in range(periods):
        window = np.array(series[-6:])
        trend  = (window[-1] - window[0]) / max(len(window) - 1, 1)
        pred   = (window * weights).sum() + trend * 0.5
        forecasts.append(max(pred, 0))
        series.append(pred)

    last_date = monthly_rev.index[-1]
    future_idx = pd.period_range(
        start=last_date + 1, periods=periods, freq="M"
    ).astype(str)
    return pd.Series(forecasts, index=future_idx)


# ─────────────────────────────────────────────────────────────────────────────
# 3. DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

COLORS = px.colors.qualitative.Bold
ACCENT = "#1F4E79"

def build_dashboard(df, out_path="outputs/sales_dashboard.html"):
    os.makedirs("outputs", exist_ok=True)

    monthly    = df.groupby("Month")[["Revenue","Orders"]].sum()
    monthly.index = pd.PeriodIndex(monthly.index, freq="M")
    monthly    = monthly.sort_index()

    forecast   = forecast_revenue(monthly["Revenue"], periods=3)
    region_rev = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
    cat_rev    = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    ch_rev     = df.groupby("Channel")["Revenue"].sum()
    heatmap_df = df.groupby(["Month","Category"])["Revenue"].sum().unstack(fill_value=0)

    # YoY
    yoy = df.groupby(["Year","Month"])["Revenue"].sum().unstack(level=0)

    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=[
            "Monthly Revenue + 3-Month Forecast",
            "Revenue by Region",
            "Revenue by Category",
            "Channel Mix",
            "Revenue Heatmap (Category × Month)",
            "Year-over-Year Revenue",
            "Monthly Order Volume",
            "Avg Revenue per Order",
            "Quarterly Revenue Breakdown"
        ],
        specs=[
            [{"colspan": 2}, None, {"type": "bar"}],
            [{"type": "pie"}, {"colspan": 2, "type": "heatmap"}, None],
            [{"type": "scatter"}, {"type": "scatter"}, {"type": "bar"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # 1. Monthly revenue + forecast
    fig.add_trace(go.Scatter(
        x=monthly.index.astype(str), y=monthly["Revenue"],
        mode="lines+markers", name="Actual Revenue",
        line=dict(color=ACCENT, width=2.5), marker=dict(size=4)
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=list(monthly.index.astype(str))[-1:] + list(forecast.index),
        y=[monthly["Revenue"].iloc[-1]] + list(forecast.values),
        mode="lines+markers", name="Forecast",
        line=dict(color="#E74C3C", width=2, dash="dash"),
        marker=dict(size=6, symbol="diamond")
    ), row=1, col=1)

    # 2. Revenue by region
    fig.add_trace(go.Bar(
        x=region_rev.index, y=region_rev.values,
        marker_color=COLORS[:len(region_rev)], showlegend=False
    ), row=1, col=3)

    # 3. Channel pie
    fig.add_trace(go.Pie(
        labels=ch_rev.index, values=ch_rev.values,
        hole=0.4, marker_colors=COLORS
    ), row=2, col=1)

    # 4. Heatmap
    # Sample last 18 months for readability
    hm = heatmap_df.iloc[-18:]
    fig.add_trace(go.Heatmap(
        z=hm.values, x=hm.columns.tolist(), y=hm.index.astype(str).tolist(),
        colorscale="Blues", showscale=True
    ), row=2, col=2)

    # 5. Monthly orders
    fig.add_trace(go.Scatter(
        x=monthly.index.astype(str), y=monthly["Orders"],
        mode="lines", name="Orders",
        line=dict(color="#27AE60", width=2), fill="tozeroy", fillcolor="rgba(39,174,96,0.1)"
    ), row=3, col=1)

    # 6. Avg revenue per order
    avg_rev = monthly["Revenue"] / monthly["Orders"]
    fig.add_trace(go.Scatter(
        x=avg_rev.index.astype(str), y=avg_rev.values,
        mode="lines+markers", name="Avg Rev/Order",
        line=dict(color="#8E44AD", width=2), marker=dict(size=4)
    ), row=3, col=2)

    # 7. Quarterly
    qtr = df.groupby(["Year","Quarter"])["Revenue"].sum().reset_index()
    qtr["Period"] = qtr["Year"].astype(str) + " " + qtr["Quarter"]
    fig.add_trace(go.Bar(
        x=qtr["Period"], y=qtr["Revenue"],
        marker_color=COLORS[:len(qtr)], showlegend=False
    ), row=3, col=3)

    fig.update_layout(
        height=1050, width=1400,
        title_text="📊 Retail Sales Analytics Dashboard — 2022–2024",
        title_font=dict(size=20, color=ACCENT),
        template="plotly_white",
        showlegend=True,
        legend=dict(x=0.01, y=0.99)
    )

    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"  ✓ Dashboard saved → {out_path}")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4. SUMMARY STATS
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(df):
    print("\n  SALES SUMMARY")
    print(f"  Period : {df['Date'].min().date()} → {df['Date'].max().date()}")
    print(f"  Total Revenue  : £{df['Revenue'].sum()/1e6:.2f}M")
    print(f"  Total Orders   : {df['Orders'].sum():,}")
    print(f"  Avg Order Value: £{df['Revenue'].sum()/df['Orders'].sum():.2f}")
    print(f"\n  Top Region   : {df.groupby('Region')['Revenue'].sum().idxmax()}")
    print(f"  Top Category : {df.groupby('Category')['Revenue'].sum().idxmax()}")
    print(f"  Top Channel  : {df.groupby('Channel')['Revenue'].sum().idxmax()}")
    yoy = df.groupby("Year")["Revenue"].sum()
    growth = (yoy.iloc[-1] / yoy.iloc[-2] - 1) * 100
    print(f"\n  YoY Revenue Growth (2023→2024): +{growth:.1f}%")


# ─────────────────────────────────────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n═══════════════════════════════════════════════")
    print("  RETAIL SALES ANALYTICS & FORECASTING PIPELINE  ")
    print("═══════════════════════════════════════════════\n")

    print("▸ Generating 3-year sales dataset …")
    df = generate_sales_data()
    os.makedirs("outputs", exist_ok=True)
    df.to_csv("outputs/retail_sales.csv", index=False)
    print(f"  ✓ {len(df):,} transaction records generated\n")

    print("▸ Computing summary statistics …")
    print_summary(df)

    print("\n▸ Building interactive dashboard …")
    build_dashboard(df)

    print("\n✅ Done! Open outputs/sales_dashboard.html in your browser.\n")
