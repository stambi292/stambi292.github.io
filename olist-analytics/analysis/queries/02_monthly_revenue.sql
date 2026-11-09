-- Monthly orders and revenue. 2016 and Sep-Oct 2018 are partial months, so they're excluded.
select
    order_month,
    count(*)                                   as orders,
    round(sum(gross_revenue), 0)               as revenue_brl,
    round(avg(gross_revenue), 2)               as avg_order_value_brl,
    round(avg(case when delivered_at is not null then is_late::int end) * 100, 1) as late_pct,
    round(avg(review_score), 2)                as avg_review_score
from marts.fact_orders
where is_valid_order
  and order_month between date '2017-01-01' and date '2018-08-01'
group by order_month
order by order_month
