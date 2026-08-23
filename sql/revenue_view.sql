CREATE VIEW monthly_revenue AS
SELECT
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
    ROUND(SUM(p.payment_value), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(SUM(p.payment_value)) OVER (ORDER BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')), 2) AS cumulative_revenue
FROM orders o
JOIN order_payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;