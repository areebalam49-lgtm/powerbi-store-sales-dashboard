-- Export your own store database to CSV files that match this project's data model.
-- Run inside the sqlite3 shell:   sqlite3 store.db < sql/export_to_csv.sql
-- Change the table and column names on the right-hand side to match YOUR schema.
-- The output column names (AS ...) must stay the same so the Power Query scripts keep working.

.headers on
.mode csv

.output data/products.csv
SELECT product_id, product_name, category, cost_price, selling_price,
       stock_qty, reorder_level, supplier_id
FROM products;

.output data/suppliers.csv
SELECT supplier_id, supplier_name, city, lead_time_days
FROM suppliers;

.output data/bills.csv
SELECT bill_id, DATE(bill_date) AS bill_date, payment_mode
FROM bills;

.output data/sale_lines.csv
SELECT line_id, bill_id, product_id, quantity, unit_price, unit_cost
FROM sale_lines;

.output data/purchases.csv
SELECT purchase_id, supplier_id, product_id,
       DATE(order_date) AS order_date, DATE(expected_date) AS expected_date,
       DATE(received_date) AS received_date, quantity, unit_cost
FROM supplier_purchases;

.output stdout
