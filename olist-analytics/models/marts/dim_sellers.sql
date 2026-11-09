-- Grain: one row per seller.
select
    s.seller_id,
    s.city,
    s.state,
    count(distinct i.order_id)  as orders,
    coalesce(sum(i.price), 0)   as revenue
from {{ ref('stg_sellers') }} s
left join {{ ref('fact_order_items') }} i
    on s.seller_id = i.seller_id
   and i.order_status not in ('canceled', 'unavailable')
group by all
