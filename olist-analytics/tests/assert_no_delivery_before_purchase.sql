select order_id, delivery_days
from {{ ref('fact_orders') }}
where delivery_days < 0
