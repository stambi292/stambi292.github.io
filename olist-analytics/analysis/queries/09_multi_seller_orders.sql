-- Orders split across several sellers arrive as separate packages. How do they review?
select
    case when sellers_count > 1 then 'Multiple sellers' else 'Single seller' end as order_type,
    count(*)                                     as orders,
    round(avg(review_score), 2)                  as avg_review_score,
    round(avg((review_score <= 2)::int) * 100, 1) as pct_bad_reviews
from marts.fact_orders
where is_valid_order and items_count > 0 and review_score is not null
group by 1
