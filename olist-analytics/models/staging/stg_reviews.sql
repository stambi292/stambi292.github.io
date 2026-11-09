-- Some orders have more than one review; keep the most recent one per order.
with ranked as (
    select
        review_id,
        order_id,
        review_score,
        review_comment_message is not null as has_comment,
        cast(review_creation_date as timestamp) as review_created_at,
        row_number() over (
            partition by order_id
            order by review_answer_timestamp desc, review_id
        ) as rn
    from {{ source('olist', 'olist_order_reviews_dataset') }}
)
select review_id, order_id, review_score, has_comment, review_created_at
from ranked
where rn = 1
