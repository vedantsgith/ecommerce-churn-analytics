CREATE VIEW customer_rfm AS
SELECT
    c.customer_unique_id,
    DATEDIFF(
        (SELECT MAX(order_purchase_timestamp) FROM orders),
        MAX(o.order_purchase_timestamp)
    ) AS recency_days,
    COUNT(DISTINCT o.order_id) AS frequency,
    SUM(p.payment_value) AS monetary
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id;