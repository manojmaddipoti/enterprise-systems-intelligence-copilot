SELECT supplier_name, blocked_invoice_amount
FROM MARTS.MART_INVOICE_EXCEPTIONS
ORDER BY blocked_invoice_amount DESC
LIMIT 10;

SELECT business_unit, total_po_amount
FROM MARTS.MART_PROCUREMENT_SPEND
ORDER BY total_po_amount DESC;
