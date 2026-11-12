"""
Print the key numbers for the CSV data so you can check your dashboard cards against them.

Usage:
    python scripts/validate_sample.py                 # checks data/sample/
    python scripts/validate_sample.py --data data     # checks your own export
"""
import argparse
import os
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "..", "data", "sample"))
d = ap.parse_args().data

p = pd.read_csv(os.path.join(d, "products.csv"))
b = pd.read_csv(os.path.join(d, "bills.csv"), parse_dates=["bill_date"])
s = pd.read_csv(os.path.join(d, "sale_lines.csv")).merge(b, on="bill_id", how="left")
pu = pd.read_csv(os.path.join(d, "purchases.csv"), parse_dates=["expected_date", "received_date"])

s["rev"] = s.quantity * s.unit_price
s["cost"] = s.quantity * s.unit_cost
rev, cost = s.rev.sum(), s.cost.sum()
bills = s.bill_id.nunique()

print("=== Overview cards ===")
print(f"Total Revenue     : Rs. {rev:,.2f}")
print(f"Gross Margin %    : {100 * (rev - cost) / rev:.2f}%")
print(f"Bills Count       : {bills:,}")
print(f"Avg Bill Value    : Rs. {rev / bills:,.2f}")
print(f"Low Stock Items   : {(p.stock_qty < p.reorder_level).sum()}")
print(f"UPI Share %       : {100 * s.loc[s.payment_mode == 'UPI', 'rev'].sum() / rev:.2f}%")

print("\n=== Revenue by month ===")
m = s.groupby(s.bill_date.dt.to_period("M")).rev.sum()
for k, v in m.items():
    print(f"{k}  Rs. {v:>12,.2f}")

print("\n=== Revenue by weekday ===")
w = s.groupby(s.bill_date.dt.day_name()).rev.sum()
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for k in order:
    print(f"{k:<10} {100 * w[k] / rev:5.1f}% of revenue")

print("\n=== Top 10 products ===")
t = s.merge(p[["product_id", "product_name"]], on="product_id").groupby("product_name").rev.sum().nlargest(10)
for k, v in t.items():
    print(f"{k:<28} Rs. {v:>11,.2f}")

print("\n=== Suppliers ===")
pu["delay"] = (pu.received_date - pu.expected_date).dt.days
g = pu.groupby("supplier_id").agg(orders=("purchase_id", "count"), avg_delay=("delay", "mean"),
                                  on_time=("delay", lambda x: 100 * (x <= 0).mean()))
print(g.round(2).to_string())
