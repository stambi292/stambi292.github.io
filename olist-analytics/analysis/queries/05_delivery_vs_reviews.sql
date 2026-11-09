-- Review score by how early/late the order arrived vs. the promised date.
select
    case
        when days_late <= -10 then '1. 10+ days early'
        when days_late <= -1  then '2. 1-9 days early'
        when days_late = 0    then '3. On the day'
        when days_late <= 3   then '4. 1-3 days late'
        when days_late <= 7   then '5. 4-7 days late'
        else                       '6. 8+ days late'
    end                                         as delivery_bucket,
    count(*)                                    as orders,
    round(avg(review_score), 2)                 as avg_review_score,
    round(avg((review_score <= 2)::int) * 100, 1) as pct_bad_reviews
from marts.fact_orders
where delivered_at is not null and review_score is not null
group by 1
order by 1
