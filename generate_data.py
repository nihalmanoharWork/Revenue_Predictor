# generate_data.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import argparse
import random
import time

def generate_rows(n_rows=10000, start_date=None, seed=None):
    """
    Generate synthetic revenue data with dynamic seed to ensure unique data each run.
    Adds timestamp column to track generation time.
    """
    # Use provided seed or fallback to current timestamp
    seed = seed or int(time.time()) % 2**32
    random.seed(seed)
    np.random.seed(seed)

    start = datetime.fromisoformat(start_date) if start_date else datetime.today() - timedelta(days=n_rows)
    rows = []

    product_ids = [f"P{str(i).zfill(3)}" for i in range(1, 51)]  # 50 products
    regions = ["North", "South", "East", "West", "Central"]
    channels = ["Online", "Retail", "Distributor"]

    base_price = {p: float(np.random.uniform(20, 300)) for p in product_ids}
    base_demand = {p: float(np.random.uniform(50, 2000)) for p in product_ids}

    for i in range(n_rows):
        date = start + timedelta(days=i)
        product = random.choice(product_ids)
        region = random.choice(regions)
        channel = random.choice(channels)

        # Seasonality factor by month
        month = date.month
        seasonality = 1 + 0.2 * np.sin(2 * np.pi * (month / 12))

        # Price variation, marketing effect, multipliers
        price = round(base_price[product] * np.random.uniform(0.9, 1.1), 2)
        marketing = round(np.random.exponential(scale=500.0), 2)
        channel_mult = {"Online": 1.1, "Retail": 0.9, "Distributor": 0.8}[channel]
        region_mult = {"North":1.05,"South":0.95,"East":1.0,"West":0.97,"Central":1.02}[region]

        units_sold = int(max(0, base_demand[product] * seasonality * channel_mult * region_mult
                             * np.exp(-0.01 * (price - base_price[product]))
                             + np.random.normal(0, 50) + 0.02 * marketing))

        revenue = round(units_sold * price + 0.1 * marketing + np.random.normal(0, 1000), 2)
        prev_revenue = round(revenue * np.random.uniform(0.85, 1.15), 2)

        rows.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Track when row generated
            "date": date.strftime("%Y-%m-%d"),
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
    
    # Ensure rows are shuffled so repeated runs look different in order
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000, help="Number of rows to generate")
    parser.add_argument("--out", type=str, default="data/revenue_data.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed")
    parser.add_argument("--start_date", type=str, default=None, help="Optional start date YYYY-MM-DD")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df = generate_rows(n_rows=args.rows, seed=args.seed, start_date=args.start_date)
    df.to_csv(args.out, index=False)
    print(f"Generated {len(df)} rows to {args.out} (seed={args.seed or 'dynamic'})")

if __name__ == "__main__":
    main()
