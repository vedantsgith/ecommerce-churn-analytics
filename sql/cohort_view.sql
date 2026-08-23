CREATE VIEW customer_cohorts AS
WITH first_purchase AS (
    SELECT
        customer_id,
        DATE_FORMAT(MIN(order_purchase_timestamp), '%Y-%m-01') AS cohort_month
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY customer_id
),
activity AS (
    SELECT
        o.customer_id,
        fp.cohort_month,
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m-01') AS order_month
    FROM orders o
    JOIN first_purchase fp ON o.customer_id = fp.customer_id
    WHERE o.order_status = 'delivered'
)
SELECT
    cohort_month,
    order_month,
    PERIOD_DIFF(DATE_FORMAT(order_month, '%Y%m'), DATE_FORMAT(cohort_month, '%Y%m')) AS month_number,
    COUNT(DISTINCT customer_id) AS active_customers
FROM activity
GROUP BY cohort_month, order_month
ORDER BY cohort_month, order_month;