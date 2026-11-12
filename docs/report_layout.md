# Report layout

Canvas: 16:9. Use one theme and at most 3–4 colours. Put a title on every visual that states the takeaway.

## Page 1 – Overview

| Area | Visual | Fields / measures |
|---|---|---|
| Top row | 4 KPI cards | Total Revenue, Gross Margin %, Bills Count, Avg Bill Value |
| Middle left | Line chart | Axis: DimDate[Month] · Values: Total Revenue, Revenue 3M Avg · Tooltip: Revenue MoM % |
| Middle right | Column chart | Axis: DimDate[Weekday] (sorted by WeekdayNo) · Value: Total Revenue |
| Bottom left | Donut or bar | Legend: FactSales[payment_mode] · Value: Total Revenue |
| Bottom right | Area chart | Running Revenue by Month |
| Left strip | Slicers | DimDate[Month] (between), DimProduct[category] (dropdown). Sync to all pages. |

## Page 2 – Products & Suppliers

| Area | Visual | Fields / measures |
|---|---|---|
| Left | Bar chart, Top N = 10 | DimProduct[product_name] · Total Revenue |
| Right | Matrix | Rows: category → product_name · Values: Total Revenue, Gross Margin %, Revenue Share % · conditional formatting on Gross Margin % |
| Bottom | Table | DimSupplier[supplier_name], Purchase Value, Purchase Orders, Avg Delay Days, On-Time Delivery % (data bars) |

**Drill-through page (hidden): Product Detail**
- Add DimProduct[product_name] to the drill-through well.
- Visuals: monthly revenue line, units sold card, stock_qty vs reorder_level card, purchase history table.
- Test: right-click a product on Page 2 → Drill through → Product Detail.

## Page 3 – Stock Alerts

| Area | Visual | Fields / measures |
|---|---|---|
| Top | Cards | Low Stock Items, total stock value |
| Main | Table | product_name, category, stock_qty, reorder_level, Avg Daily Units, Days of Cover — filtered to stock_status = "Reorder", red background when Days of Cover < 3 |
| Side | Bar chart | Low-stock count by category |
| Buttons | Bookmarks | "All items" / "Only alerts", toggling the stock_status filter |

## Final checks

- Every number on the cards matches `python scripts/validate_sample.py` (or your SQL validation queries).
- Slicers work on every page; drill-through works; no visual shows "(Blank)".
- File → Export → Export to PDF looks clean on every page.
