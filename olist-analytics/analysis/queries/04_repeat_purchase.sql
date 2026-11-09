-- How many customers come back, and how fast.
with t as (
    select customer_unique_id, purchased_at, customer_order_number
    from marts.fact_orders where is_valid_order
),
second_orders as (
    select date_diff('day', a.purchased_at, b.purchased_at) as days_to_second
    from t a
    join t b
      on a.customer_unique_id = b.customer_unique_id
     and a.customer_order_number = 1
     and b.customer_order_number = 2
)
select
    (select count(*) from marts.dim_customers where total_orders > 0)                 as customers,
    (select count(*) from marts.dim_customers where is_repeat_customer)               as repeat_customers,
    (select round(avg(is_repeat_customer::int) * 100, 2)
       from marts.dim_customers where total_orders > 0)                               as repeat_rate_pct,
    (select round(sum(case when is_repeat_customer then lifetime_revenue end)
                  / sum(lifetime_revenue) * 100, 1) from marts.dim_customers)         as repeat_revenue_share_pct,
    round(avg((days_to_second = 0)::int) * 100, 1)                                    as same_day_second_order_pct,
    median(days_to_second)                                                            as median_days_to_second_order
from second_orders
