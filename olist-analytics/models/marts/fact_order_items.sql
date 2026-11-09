-- Grain: one row per item in an order.
select
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    p.category,
    o.purchased_at,
    date_trunc('month', o.purchased_at) as order_month,
    o.order_status,
    i.price,
    i.freight_value,
    i.price + i.freight_value as item_total
from {{ ref('stg_order_items') }} i
join {{ ref('stg_orders') }} o using (order_id)
left join {{ ref('stg_products') }} p using (product_id)
