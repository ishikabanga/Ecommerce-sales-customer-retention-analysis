-- ============================================================
-- E-commerce Sales & Customer Retention Analysis — SQL Queries
-- Run against ecommerce.db (SQLite). Tables: transactions, customers
-- ============================================================

-- 1. Monthly revenue & profit with running (cumulative) total
--    Demonstrates: window function (SUM ... OVER), date functions
SELECT
    strftime('%Y-%m', order_date)                                  AS month,
    ROUND(SUM(sales), 2)                                            AS revenue,
    ROUND(SUM(profit), 2)                                           AS profit,
    ROUND(SUM(SUM(sales)) OVER (ORDER BY strftime('%Y-%m', order_date)), 2) AS cumulative_revenue
FROM transactions
GROUP BY month
ORDER BY month;

-- 2. Top 5 customers by lifetime spend, with region/segment via JOIN
--    Demonstrates: JOIN, aggregation, RANK() window function
SELECT
    t.customer_id,
    c.region,
    c.segment,
    COUNT(t.order_id)          AS total_orders,
    ROUND(SUM(t.sales), 2)     AS lifetime_spend,
    RANK() OVER (ORDER BY SUM(t.sales) DESC) AS spend_rank
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY t.customer_id, c.region, c.segment
ORDER BY lifetime_spend DESC
LIMIT 5;

-- 3. Category performance with profit-margin ranking per region
--    Demonstrates: CTE, JOIN, window function partitioned by region
WITH category_region_sales AS (
    SELECT
        c.region,
        t.category,
        SUM(t.sales)  AS revenue,
        SUM(t.profit) AS profit
    FROM transactions t
    JOIN customers c ON c.customer_id = t.customer_id
    GROUP BY c.region, t.category
)
SELECT
    region,
    category,
    ROUND(revenue, 2) AS revenue,
    ROUND(profit, 2)  AS profit,
    ROUND(100.0 * profit / revenue, 1) AS margin_pct,
    RANK() OVER (PARTITION BY region ORDER BY profit DESC) AS profit_rank_in_region
FROM category_region_sales
ORDER BY region, profit_rank_in_region;

-- 4. Customer recency, frequency, monetary (RFM) base query
--    Demonstrates: CTE, subquery, date arithmetic, aggregate functions
WITH last_order AS (
    SELECT customer_id, MAX(order_date) AS last_purchase_date
    FROM transactions
    GROUP BY customer_id
),
rfm_base AS (
    SELECT
        t.customer_id,
        JULIANDAY((SELECT MAX(order_date) FROM transactions)) - JULIANDAY(lo.last_purchase_date) AS recency_days,
        COUNT(t.order_id)      AS frequency,
        SUM(t.sales)           AS monetary
    FROM transactions t
    JOIN last_order lo ON lo.customer_id = t.customer_id
    GROUP BY t.customer_id
)
SELECT
    customer_id,
    ROUND(recency_days, 0) AS recency_days,
    frequency,
    ROUND(monetary, 2)     AS monetary,
    CASE
        WHEN recency_days <= 60 AND frequency >= 5 THEN 'Loyal / High-Value'
        WHEN recency_days > 120 AND frequency >= 3 THEN 'At-Risk'
        WHEN frequency = 1 THEN 'One-Time Buyer'
        ELSE 'Regular'
    END AS segment
FROM rfm_base
ORDER BY monetary DESC;

-- 5. Discount band vs average profit margin
--    Demonstrates: CASE binning, aggregate, HAVING
SELECT
    CASE
        WHEN discount = 0 THEN '0% (No discount)'
        WHEN discount <= 0.10 THEN '1-10%'
        WHEN discount <= 0.20 THEN '11-20%'
        ELSE '21%+'
    END AS discount_band,
    COUNT(*)                                    AS orders,
    ROUND(AVG(100.0 * profit / sales), 2)       AS avg_margin_pct
FROM transactions
GROUP BY discount_band
HAVING COUNT(*) > 5
ORDER BY avg_margin_pct DESC;
