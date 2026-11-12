# Data model

Star schema: two fact tables in the middle, three dimension tables around them.

```
   DimDate ─────┬──────────────┐
                ▼              ▼
           FactSales     FactPurchases ◄── DimSupplier
                ▲              ▲
   DimProduct ──┴──────────────┘
```

## Tables

| Table | Grain (one row = …) | Source |
|---|---|---|
| FactSales | one product line on a bill | sale_lines.csv merged with bills.csv |
| FactPurchases | one purchase order line to a supplier | purchases.csv |
| DimProduct | one product | products.csv |
| DimSupplier | one supplier | suppliers.csv |
| DimDate | one calendar day | DAX, see `dax/date_table.dax` |

## Relationships (Model view)

All are **one-to-many, single direction** (dimension filters fact).

| From (1) | To (*) |
|---|---|
| DimDate[Date] | FactSales[sale_date] |
| DimDate[Date] | FactPurchases[order_date] |
| DimProduct[product_id] | FactSales[product_id] |
| DimProduct[product_id] | FactPurchases[product_id] |
| DimSupplier[supplier_id] | FactPurchases[supplier_id] |

Optional: DimSupplier[supplier_id] → DimProduct[supplier_id] lets you slice sales by supplier. Keep it single direction.

## Housekeeping

- Hide key columns (product_id, bill_id, supplier_id, line_id) from report view.
- Hide `line_revenue` and `line_cost` and use the measures instead.
- Set number formats: currency columns to ₹ with 0 decimals, % measures to percentage with 1 decimal.
