// Power Query (M) scripts for every table.
// How to use: in Power BI Desktop, Home > Transform data > New Source > Blank Query,
// then Home > Advanced Editor, paste ONE query below, and rename the query to the name in its header.
//
// First create a text parameter called DataFolder (Home > Manage Parameters > New):
//   e.g.  C:\Users\you\Documents\GitHub\powerbi-store-sales-dashboard\data\sample\
// Point it at data\ instead of data\sample\ when you switch to your own export. Keep the trailing backslash.


// ===================== DimProduct =====================
let
    Source   = Csv.Document(File.Contents(DataFolder & "products.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers  = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Headers, {
                   {"product_id", type text}, {"product_name", type text}, {"category", type text},
                   {"cost_price", Currency.Type}, {"selling_price", Currency.Type},
                   {"stock_qty", Int64.Type}, {"reorder_level", Int64.Type}, {"supplier_id", type text}}),
    Cleaned  = Table.TransformColumns(Typed, {{"product_name", each Text.Proper(Text.Trim(_)), type text},
                                              {"category", each Text.Trim(_), type text}}),
    Dedup    = Table.Distinct(Cleaned, {"product_id"}),
    Status   = Table.AddColumn(Dedup, "stock_status", each if [stock_qty] < [reorder_level] then "Reorder" else "OK", type text)
in
    Status


// ===================== DimSupplier =====================
let
    Source  = Csv.Document(File.Contents(DataFolder & "suppliers.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed   = Table.TransformColumnTypes(Headers, {
                  {"supplier_id", type text}, {"supplier_name", type text}, {"city", type text}, {"lead_time_days", Int64.Type}})
in
    Typed


// ===================== Bills (staging, load disabled) =====================
// Right-click this query > uncheck "Enable load". It only feeds FactSales.
let
    Source  = Csv.Document(File.Contents(DataFolder & "bills.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"bill_id", type text}, {"bill_date", type date}, {"payment_mode", type text}})
in
    Typed


// ===================== FactSales =====================
let
    Source   = Csv.Document(File.Contents(DataFolder & "sale_lines.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers  = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Headers, {
                   {"line_id", Int64.Type}, {"bill_id", type text}, {"product_id", type text},
                   {"quantity", Int64.Type}, {"unit_price", Currency.Type}, {"unit_cost", Currency.Type}}),
    NoBad    = Table.SelectRows(Typed, each [quantity] <> null and [quantity] > 0 and [unit_price] <> null),
    Merged   = Table.NestedJoin(NoBad, {"bill_id"}, Bills, {"bill_id"}, "b", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Merged, "b", {"bill_date", "payment_mode"}, {"sale_date", "payment_mode"}),
    Revenue  = Table.AddColumn(Expanded, "line_revenue", each [quantity] * [unit_price], Currency.Type),
    Cost     = Table.AddColumn(Revenue, "line_cost", each [quantity] * [unit_cost], Currency.Type)
in
    Cost


// ===================== FactPurchases =====================
let
    Source  = Csv.Document(File.Contents(DataFolder & "purchases.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed   = Table.TransformColumnTypes(Headers, {
                  {"purchase_id", type text}, {"supplier_id", type text}, {"product_id", type text},
                  {"order_date", type date}, {"expected_date", type date}, {"received_date", type date},
                  {"quantity", Int64.Type}, {"unit_cost", Currency.Type}}),
    Value   = Table.AddColumn(Typed, "purchase_value", each [quantity] * [unit_cost], Currency.Type),
    Delay   = Table.AddColumn(Value, "delay_days", each Duration.Days([received_date] - [expected_date]), Int64.Type),
    OnTime  = Table.AddColumn(Delay, "on_time", each if [delay_days] <= 0 then "On time" else "Late", type text)
in
    OnTime
