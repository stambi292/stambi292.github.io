-- Top 10 product categories by revenue.
select
    main_category                               as category,
    count(*)                                    as orders,
    round(sum(gross_revenue), 0)                as revenue_brl,
    round(avg(gross_revenue), 2)                as avg_order_value_brl,
    round(avg(review_score), 2)                 as avg_review_score
from marts.fact_orders
where is_valid_order and main_category is not null
group by 1
order by revenue_brl desc
limit 10
