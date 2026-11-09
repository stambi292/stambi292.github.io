-- Does a late FIRST delivery make customers less likely to return?
-- Only first orders placed before Mar 2018, so every customer had 6+ months to come back.
select
    case when o.is_late then 'Late first delivery' else 'On-time first delivery' end as first_order,
    count(*)                                             as customers,
    round(avg(c.is_repeat_customer::int) * 100, 2)       as repeat_rate_pct
from marts.fact_orders o
join marts.dim_customers c using (customer_unique_id)
where o.customer_order_number = 1
  and o.is_valid_order
  and o.delivered_at is not null
  and o.purchased_at < timestamp '2018-03-01'
group by 1
order by 1 desc
