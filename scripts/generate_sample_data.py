"""
Generate a SAMPLE dataset for the Store Sales & Inventory Dashboard.

This is synthetic data with the same shape as a small general-store database
(about 32,000 bills and 90,000 sale lines over 12 months). Use it to build and
test the dashboard, then replace it with your own export (see sql/export_to_csv.sql).

Usage:
    python scripts/generate_sample_data.py            # writes to data/sample/
    python scripts/generate_sample_data.py --seed 7   # different random data
"""
import argparse
import csv
import os
import random
from datetime import date, timedelta

CATEGORIES = {
    "Staples": [("Basmati Rice 1kg", 95, 120), ("Sona Masoori Rice 5kg", 290, 340), ("Wheat Atta 5kg", 210, 255),
                ("Toor Dal 1kg", 125, 155), ("Moong Dal 1kg", 105, 135), ("Chana Dal 1kg", 80, 102),
                ("Rajma 500g", 70, 92), ("Kabuli Chana 1kg", 95, 125), ("Besan 500g", 45, 60), ("Poha 500g", 28, 40),
                ("Suji 500g", 24, 34), ("Sugar 1kg", 40, 48), ("Salt 1kg", 18, 25), ("Jaggery 1kg", 55, 72)],
    "Oils & Ghee": [("Mustard Oil 1L", 140, 168), ("Sunflower Oil 1L", 125, 150), ("Soybean Oil 1L", 115, 138),
                    ("Groundnut Oil 1L", 175, 210), ("Desi Ghee 500ml", 280, 325), ("Vanaspati 1L", 120, 142)],
    "Spices": [("Turmeric Powder 200g", 32, 45), ("Red Chilli Powder 200g", 45, 62), ("Coriander Powder 200g", 30, 42),
               ("Garam Masala 100g", 48, 68), ("Cumin Seeds 100g", 38, 55), ("Black Pepper 50g", 45, 65),
               ("Mustard Seeds 100g", 15, 24), ("Hing 25g", 40, 58)],
    "Beverages": [("Tea Leaves 500g", 190, 235), ("Instant Coffee 100g", 230, 285), ("Green Tea 25 bags", 110, 145),
                  ("Glucose Drink 500g", 165, 205), ("Cold Drink 750ml", 30, 40), ("Fruit Juice 1L", 85, 110),
                  ("Packaged Water 1L", 14, 20)],
    "Snacks": [("Glucose Biscuits 250g", 22, 30), ("Cream Biscuits 150g", 25, 35), ("Salted Chips 90g", 15, 20),
               ("Namkeen Mix 400g", 70, 95), ("Rusk 300g", 35, 48), ("Instant Noodles 4-pack", 48, 60),
               ("Cornflakes 475g", 155, 195), ("Chocolate Bar 50g", 38, 50), ("Peanut Chikki 200g", 30, 45)],
    "Dairy & Bakery": [("Milk 1L", 54, 62), ("Curd 400g", 30, 38), ("Paneer 200g", 75, 92), ("Butter 100g", 50, 58),
                       ("Bread 400g", 32, 42), ("Brown Bread 400g", 40, 52), ("Eggs 6-pack", 38, 48), ("Cheese Slices 200g", 110, 135)],
    "Personal Care": [("Bath Soap 100g", 28, 40), ("Shampoo 180ml", 105, 140), ("Toothpaste 150g", 70, 95),
                      ("Toothbrush", 18, 30), ("Hair Oil 200ml", 80, 110), ("Face Wash 100ml", 95, 135),
                      ("Talcum Powder 100g", 60, 85), ("Shaving Cream 70g", 45, 65)],
    "Household": [("Detergent Powder 1kg", 85, 115), ("Dishwash Bar 200g", 15, 22), ("Dishwash Liquid 500ml", 80, 110),
                  ("Floor Cleaner 1L", 110, 150), ("Toilet Cleaner 500ml", 70, 95), ("Mosquito Coil 10pc", 30, 45),
                  ("Agarbatti Pack", 25, 40), ("Matchbox 10-pack", 8, 12), ("Garbage Bags 30pc", 55, 80)],
}

SUPPLIERS = [
    ("S01", "Sample Supplier A (Staples)", "New Delhi", 3, ["Staples"]),
    ("S02", "Sample Supplier B (Oils)", "Ghaziabad", 4, ["Oils & Ghee"]),
    ("S03", "Sample Supplier C (Spices)", "New Delhi", 5, ["Spices"]),
    ("S04", "Sample Supplier D (Beverages)", "Noida", 4, ["Beverages"]),
    ("S05", "Sample Supplier E (Snacks)", "Gurugram", 3, ["Snacks"]),
    ("S06", "Sample Supplier F (Dairy)", "New Delhi", 1, ["Dairy & Bakery"]),
    ("S07", "Sample Supplier G (Personal Care)", "Faridabad", 6, ["Personal Care"]),
    ("S08", "Sample Supplier H (Household)", "Noida", 5, ["Household"]),
]

START = date(2025, 11, 1)
END = date(2026, 10, 31)
WEEKDAY_FACTOR = [0.85, 0.82, 0.86, 0.90, 1.05, 1.35, 1.17]  # Mon..Sun
FESTIVE = {10: 1.25, 11: 1.15, 3: 1.08}  # month -> uplift (Diwali / Holi season)
PAYMENT = [("Cash", 0.42), ("UPI", 0.48), ("Card", 0.10)]


def weighted(choices):
    r, acc = random.random(), 0.0
    for v, w in choices:
        acc += w
        if r <= acc:
            return v
    return choices[-1][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data", "sample"))
    a = ap.parse_args()
    random.seed(a.seed)
    os.makedirs(a.out, exist_ok=True)

    # ---- products
    cat_supplier = {c: s[0] for s in SUPPLIERS for c in s[4]}
    products, pid = [], 1
    for cat, items in CATEGORIES.items():
        for name, cost, price in items:
            popularity = random.uniform(0.4, 2.2) * (1.6 if cat in ("Dairy & Bakery", "Staples") else 1.0)
            reorder = random.randint(8, 30)
            products.append(dict(product_id=f"P{pid:03d}", product_name=name, category=cat,
                                 cost_price=cost, selling_price=price, reorder_level=reorder,
                                 supplier_id=cat_supplier[cat], _pop=popularity))
            pid += 1
    weights = [p["_pop"] for p in products]

    # ---- bills + sale lines
    bills, lines, line_id, bill_no = [], [], 1, 1
    sold = {p["product_id"]: 0 for p in products}
    d = START
    while d <= END:
        n = int(random.gauss(88, 9) * WEEKDAY_FACTOR[d.weekday()] * FESTIVE.get(d.month, 1.0))
        for _ in range(max(n, 20)):
            bid = f"B{bill_no:06d}"
            bills.append(dict(bill_id=bid, bill_date=d.isoformat(), payment_mode=weighted(PAYMENT)))
            k = max(1, min(9, int(random.expovariate(1 / 2.3)) + 1))
            for p in random.choices(products, weights=weights, k=k):
                q = 1 if random.random() < 0.75 else random.randint(2, 4)
                # small price drift through the year
                price = round(p["selling_price"] * (1 + 0.04 * (d - START).days / 365), 2)
                lines.append(dict(line_id=line_id, bill_id=bid, product_id=p["product_id"], quantity=q,
                                  unit_price=price, unit_cost=p["cost_price"]))
                sold[p["product_id"]] += q
                line_id += 1
            bill_no += 1
        d += timedelta(days=1)

    # ---- purchases (restocking roughly every 1-3 weeks per product)
    purchases, pur_id = [], 1
    lead = {s[0]: s[3] for s in SUPPLIERS}
    for p in products:
        yearly = sold[p["product_id"]]
        orders = max(4, yearly // max(1, int(yearly / 26) or 1) if yearly else 4)
        orders = min(orders, 40)
        qty = max(5, int(yearly / orders * random.uniform(0.95, 1.15)))
        for i in range(orders):
            od = START + timedelta(days=int(i * 365 / orders) + random.randint(0, 3))
            if od > END:
                break
            exp = od + timedelta(days=lead[p["supplier_id"]])
            delay = 0 if random.random() < 0.7 else random.randint(1, 6)
            purchases.append(dict(purchase_id=f"PO{pur_id:05d}", supplier_id=p["supplier_id"], product_id=p["product_id"],
                                  order_date=od.isoformat(), expected_date=exp.isoformat(),
                                  received_date=(exp + timedelta(days=delay)).isoformat(),
                                  quantity=qty, unit_cost=p["cost_price"]))
            pur_id += 1

    # closing stock as of END (some items deliberately below reorder level)
    for p in products:
        p["stock_qty"] = random.randint(0, p["reorder_level"] - 1) if random.random() < 0.18 else \
            random.randint(p["reorder_level"], p["reorder_level"] * 5)

    def write(name, rows, cols):
        with open(os.path.join(a.out, name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    write("products.csv", products, ["product_id", "product_name", "category", "cost_price", "selling_price",
                                     "stock_qty", "reorder_level", "supplier_id"])
    write("suppliers.csv", [dict(supplier_id=s[0], supplier_name=s[1], city=s[2], lead_time_days=s[3]) for s in SUPPLIERS],
          ["supplier_id", "supplier_name", "city", "lead_time_days"])
    write("bills.csv", bills, ["bill_id", "bill_date", "payment_mode"])
    write("sale_lines.csv", lines, ["line_id", "bill_id", "product_id", "quantity", "unit_price", "unit_cost"])
    write("purchases.csv", purchases, ["purchase_id", "supplier_id", "product_id", "order_date", "expected_date",
                                       "received_date", "quantity", "unit_cost"])
    print(f"products={len(products)} suppliers={len(SUPPLIERS)} bills={len(bills)} "
          f"sale_lines={len(lines)} purchases={len(purchases)} -> {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
