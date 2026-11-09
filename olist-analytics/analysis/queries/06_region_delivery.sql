-- Delivery speed, lateness, freight burden and satisfaction by customer region.
select
    case
        when customer_state = 'SP' then 'São Paulo'
        when customer_state in ('RJ','MG','ES') then 'Southeast (ex-SP)'
        when customer_state in ('PR','SC','RS') then 'South'
        when customer_state in ('DF','GO','MT','MS') then 'Center-West'
        when customer_state in ('BA','PE','CE','MA','PB','RN','PI','AL','SE') then 'Northeast'
        else 'North'
    end                                          as region,
    count(*)                                     as orders,
    round(sum(gross_revenue), 0)                 as revenue_brl,
    round(avg(delivery_days), 1)                 as avg_delivery_days,
    round(avg(case when delivered_at is not null then is_late::int end) * 100, 1) as late_pct,
    round(sum(freight_value) / sum(gross_revenue) * 100, 1) as freight_share_pct,
    round(avg(review_score), 2)                  as avg_review_score
from marts.fact_orders
where is_valid_order
group by 1
order by orders desc
