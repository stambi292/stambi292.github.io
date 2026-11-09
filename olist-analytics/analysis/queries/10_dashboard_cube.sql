-- Pre-aggregated data for the interactive dashboard filters (month x region x category x delivery bucket).
-- The page sums these rows for whatever filters the viewer picks. Categories outside the top 15 by revenue become "other".
with top_categories as (
    select main_category
    from marts.fact_orders
    where is_valid_order and main_category is not null
    group by 1
    order by sum(gross_revenue) desc
    limit 15
),
orders as (
    select
        strftime(order_month, '%Y-%m') as month,
        case
            when customer_state = 'SP' then 'São Paulo'
            when customer_state in ('RJ','MG','ES') then 'Southeast (ex-SP)'
            when customer_state in ('PR','SC','RS') then 'South'
            when customer_state in ('DF','GO','MT','MS') then 'Center-West'
            when customer_state in ('BA','PE','CE','MA','PB','RN','PI','AL','SE') then 'Northeast'
            else 'North'
        end as region,
        case when main_category in (select main_category from top_categories)
             then main_category else 'other' end as category,
        case
            when delivered_at is null then null
            when days_late <= -10 then 1
            when days_late <= -1  then 2
            when days_late = 0    then 3
            when days_late <= 3   then 4
            when days_late <= 7   then 5
            else 6
        end as delivery_bucket,
        gross_revenue, freight_value, review_score, is_late, delivery_days
    from marts.fact_orders
    where is_valid_order
      and order_month between date '2017-01-01' and date '2018-08-01'
)
select
    month, region, category, delivery_bucket,
    count(*)                                         as orders,
    round(sum(gross_revenue), 2)                     as revenue,
    round(sum(freight_value), 2)                     as freight,
    count(review_score)                              as reviews,
    coalesce(sum(review_score), 0)                   as review_sum,
    count_if(review_score <= 2)                      as bad_reviews,
    count(delivery_days)                             as delivered,
    coalesce(sum(delivery_days), 0)                  as delivery_days_sum,
    count_if(is_late)                                as late
from orders
group by all
order by month, region, category, delivery_bucket
