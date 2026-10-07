# E-commerce Sales & Customer Retention Analysis

**A Python + SQL data analytics project analyzing 2 years of e-commerce transactions to identify revenue trends, profit leaks, and at-risk customers — with concrete, actionable recommendations.**

---

## 1. Business Problem

A mid-size e-commerce retailer wants to understand:
1. Where its revenue and profit are actually coming from (category / region)
2. Whether its discounting strategy is helping or hurting profitability
3. Which customers are at risk of churning, and how much revenue is at stake

## 2. Dataset

- 6,200 transactions | 832 customers | Jan 2024 – Dec 2025
- Fields: order date, customer, region, category, product, quantity, discount, sales, profit, shipment mode
- (`data/ecommerce_transactions.csv`, `data/customers_reference.csv`)

## 3. Tools & Techniques

| Area | Tools / Techniques used |
|---|---|
| Data cleaning & validation | Python (Pandas) — duplicate removal, null handling, type checks |
| Querying | SQL (SQLite) — JOINs, CTEs, window functions (`RANK`, running `SUM OVER`), CASE-based binning |
| Analysis | Trend analysis, category/regional profitability, discount-margin correlation |
| Customer analytics | **RFM segmentation** (Recency, Frequency, Monetary) to flag churn risk |
| Visualization | Matplotlib / Seaborn |

## 4. Key Insights

1. **₹2.2 Cr in revenue analysed** across 6,200 orders and 832 customers.
2. **Furniture is the top revenue category** (₹79.9L, 18.7% margin) — but Apparel has the healthiest margins per rupee of discount given.
3. **Discounting is actively eroding profit**: discount level and profit margin have a **-0.56 correlation** — orders discounted above ~20% frequently approach break-even.
4. **85 customers (10%) are "At-Risk"** — previously frequent buyers who've gone quiet — representing **10.5% of total historical revenue**. This is a concrete, sized target for a win-back email/retention campaign.
5. **39% of the customer base has already churned** (no purchase in a long time, low historical frequency) vs. **29% are Loyal/High-Value** — meaning retention efforts should be prioritized before acquisition spend.
6. Clear **seasonality**: Oct–Dec (festive season) and July (mid-year sale) show consistent revenue spikes — useful for inventory and staffing planning.

See `insights_summary.txt` for the auto-generated numeric summary and `/charts` for all visuals.

## 5. Recommendations (what I'd tell a stakeholder)

- **Cap discounts near 10–15%** for categories with thin margins (Electronics) — beyond that, profit contribution turns negative.
- **Launch a targeted win-back campaign** for the 85 At-Risk customers before they fully churn — they're worth ~10.5% of revenue.
- **Double down on Furniture and Home & Kitchen** in Oct–Dec inventory planning given the consistent seasonal lift.
- **Investigate the East region's margin gap** vs. North — likely a discount-policy or shipping-cost issue worth a follow-up analysis.

## 6. How to reproduce

```bash
pip install pandas numpy matplotlib seaborn
python generate_data.py      # builds the synthetic dataset
python analysis.py           # cleans data, runs EDA, builds all charts + insights
```

SQL queries (joins, CTEs, window functions) are in `sql/analysis_queries.sql` and can be run against `sql/ecommerce.db` (SQLite) or adapted directly to PostgreSQL/MySQL.

## 7. Project Structure

```
├── generate_data.py              # synthetic but realistic dataset generator
├── analysis.py                   # full analysis pipeline
├── data/
│   ├── ecommerce_transactions.csv
│   ├── customers_reference.csv
│   ├── monthly_summary.csv
│   ├── category_summary.csv
│   ├── region_summary.csv
│   ├── customer_rfm_segments.csv
│   └── segment_counts.csv
├── sql/
│   ├── analysis_queries.sql      # joins, CTEs, window functions
│   └── ecommerce.db              # SQLite DB used to validate the queries
├── charts/
│   ├── 01_monthly_trend.png
│   ├── 02_category_revenue.png
│   ├── 03_region_margin.png
│   ├── 04_discount_vs_margin.png
│   └── 05_rfm_segments.png
└── insights_summary.txt
```

---
**Note on the data:** transaction records are synthetically generated (with realistic seasonality, regional, and customer-loyalty patterns baked in) rather than a public dataset, so the analysis, code, and insights above are entirely original work — safe to discuss in depth in an interview.

