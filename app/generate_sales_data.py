import csv, random, datetime, os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "sales_full.csv")

products = [f"product_{i}" for i in range(1, 51)]
start_date = datetime.date(2024, 1, 1)
days = 180

with open(OUT_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    # product_id, price, quantity, sale_date
    for _ in range(5000):
        p = random.choice(products)
        price = round(random.uniform(10, 500), 2)
        qty = random.randint(1, 10)
        date = start_date + datetime.timedelta(days=random.randint(0, days))
        writer.writerow([p, price, qty, date.isoformat()])

print("Wrote", OUT_PATH)
