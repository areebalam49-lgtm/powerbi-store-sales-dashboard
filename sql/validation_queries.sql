-- Run these in SQLite and compare the results with the dashboard cards.
-- If they match, your Power BI model and DAX measures are correct.

-- 1. Total revenue, cost and gross margin %
SELECT ROUND(SUM(quantity * unit_price), 2)                       AS total_revenue,
       ROUND(SUM(quantity * unit_cost), 2)                        AS total_cost,
       ROUND(100.0 * SUM(quantity * (unit_price - unit_cost))
                   / SUM(quantity * unit_price), 2)               AS gross_margin_pct
FROM sale_lines;

-- 2. Revenue by month
SELECT STRFTIME('%Y-%m', b.bill_date) AS month,
       ROUND(SUM(s.quantity * s.unit_price), 2) AS revenue
FROM sale_lines s JOIN bills b ON b.bill_id = s.bill_id
GROUP BY month ORDER BY month;

-- 3. Top 10 products by revenue
SELECT p.product_name, ROUND(SUM(s.quantity * s.unit_price), 2) AS revenue
FROM sale_lines s JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_name ORDER BY revenue DESC LIMIT 10;

-- 4. Average bill value
SELECT ROUND(SUM(quantity * unit_price) / COUNT(DISTINCT bill_id), 2) AS avg_bill_value
FROM sale_lines;

-- 5. Products below reorder level
SELECT product_name, stock_qty, reorder_level
FROM products WHERE stock_qty < reorder_level ORDER BY stock_qty;

-- 6. Average supplier delay (days late vs expected)
SELECT supplier_id,
       ROUND(AVG(JULIANDAY(received_date) - JULIANDAY(expected_date)), 2) AS avg_delay_days
FROM supplier_purchases GROUP BY supplier_id ORDER BY avg_delay_days DESC;
