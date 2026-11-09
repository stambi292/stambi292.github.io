-- Headline KPIs (valid orders = not canceled/unavailable)
select
    count(*)                                   as orders,
    count(distinct customer_unique_id)         as customers,
    round(sum(gross_revenue), 0)               as revenue_brl,
    round(avg(gross_revenue), 2)               as avg_order_value_brl,
    round(avg(review_score), 2)                as avg_review_score,
    round(avg(case when delivered_at is not null then is_late::int end) * 100, 1) as late_delivery_pct,
    round(avg(delivery_days), 1)               as avg_delivery_days,
    round(avg(promised_days), 1)               as avg_promised_days
from marts.fact_orders
where is_valid_order
