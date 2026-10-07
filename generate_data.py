"""
generate_data.py
Generates a realistic 2-year e-commerce transactions dataset with seasonality,
regional patterns, discount behaviour, and customer-level repeat-purchase patterns
so that downstream RFM / churn-risk / trend analysis produces genuine, non-trivial insights.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)

N_CUSTOMERS = 850
N_ORDERS = 6200
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days

regions = ["North", "South", "East", "West", "Central"]
region_weights = [0.22, 0.24, 0.18, 0.20, 0.16]

segments = ["Consumer", "Corporate", "Home Office"]
segment_weights = [0.55, 0.30, 0.15]

categories = {
    "Electronics": ["Headphones", "Smartwatch", "Bluetooth Speaker", "Power Bank", "Webcam"],
    "Furniture": ["Office Chair", "Study Table", "Bookshelf", "Bed Frame", "Sofa"],
    "Apparel": ["T-Shirt", "Jacket", "Running Shoes", "Jeans", "Cap"],
    "Home & Kitchen": ["Mixer Grinder", "Cookware Set", "Air Fryer", "Vacuum Cleaner", "Lamp"],
    "Stationery & Office": ["Notebook Pack", "Printer Ink", "Desk Organizer", "Pen Set", "File Folder"],
}
category_base_price = {
    "Electronics": 2800, "Furniture": 6200, "Apparel": 900,
    "Home & Kitchen": 3200, "Stationery & Office": 350,
}
category_margin = {
    "Electronics": 0.18, "Furniture": 0.22, "Apparel": 0.35,
    "Home & Kitchen": 0.20, "Stationery & Office": 0.30,
}

ship_modes = ["Standard", "Express", "Same Day"]
ship_weights = [0.62, 0.28, 0.10]

# ---- Customers with different loyalty archetypes so churn/RFM shows real signal ----
# 15% "loyal" (frequent, recent), 45% "regular", 25% "at-risk" (used to buy, stopped),
# 15% "one-time" (single purchase, long ago)
archetypes = rng.choice(
    ["loyal", "regular", "at_risk", "one_time"],
    size=N_CUSTOMERS,
    p=[0.15, 0.45, 0.25, 0.15],
)
customer_region = rng.choice(regions, size=N_CUSTOMERS, p=region_weights)
customer_segment = rng.choice(segments, size=N_CUSTOMERS, p=segment_weights)
customer_ids = [f"CUST-{i:05d}" for i in range(1, N_CUSTOMERS + 1)]

# assign each customer a purchase-count weight based on archetype (drives N_ORDERS distribution)
archetype_order_weight = {"loyal": 9, "regular": 4, "at_risk": 2.5, "one_time": 1}
cust_weights = np.array([archetype_order_weight[a] for a in archetypes], dtype=float)
cust_weights = cust_weights / cust_weights.sum()

order_customer_idx = rng.choice(N_CUSTOMERS, size=N_ORDERS, p=cust_weights)

rows = []
order_counter = 1
for idx in order_customer_idx:
    cust_id = customer_ids[idx]
    arche = archetypes[idx]
    region = customer_region[idx]
    segment = customer_segment[idx]

    # date distribution depends on archetype (at_risk/one_time cluster earlier)
    if arche == "loyal":
        day_offset = rng.integers(0, TOTAL_DAYS)
        # bias toward recent days
        day_offset = int(TOTAL_DAYS * (rng.beta(2.5, 1.2)))
    elif arche == "regular":
        day_offset = int(TOTAL_DAYS * rng.beta(1.6, 1.4))
    elif arche == "at_risk":
        day_offset = int(TOTAL_DAYS * rng.beta(1.2, 3.0))  # clustered in first ~40% of window
    else:  # one_time
        day_offset = int(TOTAL_DAYS * rng.beta(1.0, 4.5))  # clustered very early

    order_date = START_DATE + timedelta(days=day_offset)

    # seasonality bump: Oct-Dec (festive/holiday season) and July (mid-year sale)
    month = order_date.month
    seasonal_multiplier = 1.35 if month in (10, 11, 12) else (1.15 if month == 7 else 1.0)

    category = rng.choice(list(categories.keys()), p=[0.28, 0.16, 0.24, 0.20, 0.12])
    product = rng.choice(categories[category])
    base_price = category_base_price[category] * rng.uniform(0.75, 1.3)

    quantity = int(rng.choice([1, 1, 1, 2, 2, 3], p=[0.45, 0.2, 0.15, 0.1, 0.06, 0.04]))
    discount = float(rng.choice([0, 0, 0.05, 0.1, 0.15, 0.2, 0.3],
                                 p=[0.35, 0.15, 0.15, 0.15, 0.1, 0.07, 0.03]))

    gross_sales = base_price * quantity * seasonal_multiplier
    sales = round(gross_sales * (1 - discount), 2)
    margin = category_margin[category] - (discount * 0.6)  # heavy discounts erode margin
    profit = round(sales * margin, 2)

    ship_mode = rng.choice(ship_modes, p=ship_weights)

    rows.append({
        "order_id": f"ORD-{order_counter:06d}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "customer_id": cust_id,
        "customer_segment": segment,
        "region": region,
        "category": category,
        "product_name": product,
        "quantity": quantity,
        "discount": discount,
        "sales": sales,
        "profit": profit,
        "ship_mode": ship_mode,
    })
    order_counter += 1

df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
df.to_csv("data/ecommerce_transactions.csv", index=False)

# also save a customer reference table (useful for the SQL join demo)
cust_df = pd.DataFrame({
    "customer_id": customer_ids,
    "region": customer_region,
    "segment": customer_segment,
    "archetype": archetypes,  # ground-truth label, kept only for validation, not used in analysis
})
cust_df.to_csv("data/customers_reference.csv", index=False)

print(f"Generated {len(df)} transactions for {N_CUSTOMERS} customers")
print(df.head())
