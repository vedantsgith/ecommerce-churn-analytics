CREATE VIEW customer_features AS
SELECT
    c.customer_unique_id,
    AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)) AS avg_delivery_days,
    COUNT(DISTINCT pr.product_category_name_english) AS category_diversity,
    AVG(pay.payment_installments) AS avg_installments
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products pr ON oi.product_id = pr.product_id
JOIN order_payments pay ON o.order_id = pay.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id;