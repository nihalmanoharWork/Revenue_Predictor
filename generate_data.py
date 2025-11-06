# generate_data.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import argparse
import random

def generate_rows(n_rows=10000, start_date="2020-01-01", seed=42):
    random.seed(seed)
    np.random.seed(seed)

    start = datetime.fromisoformat(start_date)
    rows = []
    product_ids = [f"P{str(i).zfill(3)}" for i in range(1, 51)]  # 50 products
    regions = ["North", "South", "East", "West", "Central"]
    channels = ["Online", "Retail", "Distributor"]
    base_price = {p: float(np.random.uniform(20, 300)) for p in product_ids}
    base_demand = {p: float(np.random.uniform(50, 2000)) for p in product_ids}

    for i in range(n_rows):
        # monthly dates across span
        date = start + timedelta(days=int(i % 365 * (365 / 12) / 30))  # approximate monthly variety
        product = random.choice(product_ids)
        region = random.choice(regions)
        channel = random.choice(channels)

        # seasonality factor (sinusoidal by month)
        month = (start.month + (i % 36)) % 12 + 1
        seasonality = 1 + 0.2 * np.sin(2 * np.pi * (month / 12))

        # randomness and marketing effect
        price = round(base_price[product] * np.random.uniform(0.9, 1.1), 2)
        marketing = round(np.random.exponential(scale=500.0), 2)
        # channel multipliers
        channel_mult = {"Online": 1.1, "Retail": 0.9, "Distributor": 0.8}[channel]
        region_mult = {"North":1.05,"South":0.95,"East":1.0,"West":0.97,"Central":1.02}[region]

        units_sold = int(max(0, base_demand[product] * seasonality * channel_mult * region_mult
                             * np.exp(-0.01 * (price - base_price[product]))
                             + np.random.normal(0, 50) + 0.02 * marketing))

        revenue = round(units_sold * price + 0.1 * marketing + np.random.normal(0, 1000), 2)

        # previous month revenue (lag), use some smoothing
        prev_revenue = round(revenue * np.random.uniform(0.85, 1.15), 2)

        rows.append({
            "date": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
            "product_id": product,
            "region": region,
            "channel": channel,
            "price": price,
            "marketing_spend": marketing,
            "units_sold": units_sold,
            "prev_month_revenue": prev_revenue,
            "revenue": revenue
        })

    df = pd.DataFrame(rows)
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000, help="Number of rows to generate")
    parser.add_argument("--out", type=str, default="data/revenue_data.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df = generate_rows(n_rows=args.rows, seed=args.seed)
    df.to_csv(args.out, index=False)
    print(f"Generated {len(df)} rows to {args.out}")

if __name__ == "__main__":
    main()
