-- Grain: one row per real customer (customer_unique_id).
with orders as (
    select * from {{ ref('fact_orders') }} where is_valid_order
),

latest_location as (
    select
        c.customer_unique_id,
        arg_max(c.city,  o.purchased_at) as city,
        arg_max(c.state, o.purchased_at) as state
    from {{ ref('stg_customers') }} c
    join {{ ref('stg_orders') }} o using (customer_id)
    group by c.customer_unique_id
)

select
    l.customer_unique_id,
    l.city,
    l.state,
    min(o.purchased_at)                     as first_order_at,
    max(o.purchased_at)                     as last_order_at,
    date_trunc('month', min(o.purchased_at)) as cohort_month,
    count(o.order_id)                       as total_orders,
    coalesce(sum(o.gross_revenue), 0)       as lifetime_revenue,
    avg(o.review_score)                     as avg_review_score,
    count(o.order_id) > 1                   as is_repeat_customer
from latest_location l
left join orders o using (customer_unique_id)
group by all
