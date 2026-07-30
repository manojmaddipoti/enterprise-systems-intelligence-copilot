SELECT supplier_name, SUM(blocked_invoice_amount) AS blocked_invoice_amount
FROM MARTS.MART_INVOICE_EXCEPTIONS
GROUP BY supplier_name
ORDER BY blocked_invoice_amount DESC
LIMIT 10;

SELECT business_unit, total_po_amount
FROM MARTS.MART_PROCUREMENT_SPEND
ORDER BY total_po_amount DESC;

SELECT business_unit, workflow_health_score, match_rate, blocked_invoice_amount
FROM MARTS.MART_ENTERPRISE_WORKFLOW_HEALTH
ORDER BY workflow_health_score ASC
LIMIT 10;

SELECT approver_role, approver_name, overdue_count, total_amount_pending
FROM MARTS.MART_APPROVAL_BOTTLENECKS
ORDER BY bottleneck_score DESC
LIMIT 10;
