CREATE VIEW customer_cohorts AS
WITH first_purchase AS (
    SELECT
        c.customer_unique_id,
        DATE_FORMAT(MIN(o.order_purchase_timestamp), '%Y-%m-01') AS cohort_month
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
activity AS (
    SELECT
        c.customer_unique_id,
        fp.cohort_month,
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m-01') AS order_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN first_purchase fp ON c.customer_unique_id = fp.customer_unique_id
    WHERE o.order_status = 'delivered'
)
SELECT
    cohort_month,
    order_month,
    PERIOD_DIFF(DATE_FORMAT(order_month, '%Y%m'), DATE_FORMAT(cohort_month, '%Y%m')) AS month_number,
    COUNT(DISTINCT customer_unique_id) AS active_customers
FROM activity
GROUP BY cohort_month, order_month
ORDER BY cohort_month, order_month;