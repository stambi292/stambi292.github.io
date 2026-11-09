-- Grain: one row per order.
with items as (
    select
        order_id,
        count(*)                  as items_count,
        count(distinct seller_id) as sellers_count,
        sum(price)                as items_value,
        sum(freight_value)        as freight_value,
        -- category that makes up most of the order value
        arg_max(category, price)  as main_category
    from {{ ref('fact_order_items') }}
    group by order_id
),

payments as (
    select
        order_id,
        sum(payment_value)                 as payment_value,
        arg_max(payment_type, payment_value) as main_payment_type,
        max(payment_installments)          as installments
    from {{ ref('stg_payments') }}
    group by order_id
),

base as (
    select
        o.order_id,
        c.customer_unique_id,
        c.state as customer_state,
        o.order_status,
        o.order_status not in ('canceled', 'unavailable') as is_valid_order,
        o.purchased_at,
        date_trunc('month', o.purchased_at) as order_month,
        o.delivered_at,
        o.estimated_delivery_at,

        coalesce(i.items_count, 0)   as items_count,
        coalesce(i.sellers_count, 0) as sellers_count,
        i.main_category,
        coalesce(i.items_value, 0)   as items_value,
        coalesce(i.freight_value, 0) as freight_value,
        coalesce(i.items_value, 0) + coalesce(i.freight_value, 0) as gross_revenue,
        p.payment_value,
        p.main_payment_type,
        p.installments,

        r.review_score,
        r.has_comment as review_has_comment,

        -- delivery metrics (delivered orders only)
        date_diff('day', o.purchased_at, o.delivered_at)          as delivery_days,
        date_diff('day', o.purchased_at, o.estimated_delivery_at) as promised_days,
        date_diff('day', cast(o.estimated_delivery_at as date),
                         cast(o.delivered_at as date))            as days_late
    from {{ ref('stg_orders') }} o
    join {{ ref('stg_customers') }} c using (customer_id)
    left join items    i using (order_id)
    left join payments p using (order_id)
    left join {{ ref('stg_reviews') }} r using (order_id)
)

select
    *,
    case when delivered_at is null then null else days_late > 0 end as is_late,
    row_number() over (
        partition by customer_unique_id
        order by purchased_at, order_id
    ) as customer_order_number
from base
