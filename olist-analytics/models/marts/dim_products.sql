-- Grain: one row per product.
select
    p.product_id,
    p.category,
    p.category_pt,
    p.photos_qty,
    p.weight_g,
    p.volume_cm3,
    count(i.order_item_id)          as units_sold,
    coalesce(sum(i.price), 0)       as revenue,
    avg(i.price)                    as avg_price
from {{ ref('stg_products') }} p
left join {{ ref('fact_order_items') }} i
    on p.product_id = i.product_id
   and i.order_status not in ('canceled', 'unavailable')
group by all
