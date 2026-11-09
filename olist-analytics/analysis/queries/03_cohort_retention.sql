-- Share of each monthly cohort that placed another order N months after their first.
with orders as (
    select o.customer_unique_id, o.order_month, c.cohort_month
    from marts.fact_orders o
    join marts.dim_customers c using (customer_unique_id)
    where o.is_valid_order
),
activity as (
    select distinct
        cohort_month,
        customer_unique_id,
        date_diff('month', cohort_month, order_month) as months_since_first
    from orders
),
cohort_size as (
    select cohort_month, count(*) as customers
    from activity where months_since_first = 0
    group by cohort_month
)
select
    a.cohort_month,
    s.customers                             as cohort_customers,
    a.months_since_first,
    count(*)                                as active_customers,
    round(count(*) * 100.0 / s.customers, 2) as retention_pct
from activity a
join cohort_size s using (cohort_month)
where a.cohort_month between date '2017-01-01' and date '2018-07-01'  -- Aug 2018 has no follow-up month yet
  and a.months_since_first between 1 and 12
group by a.cohort_month, s.customers, a.months_since_first
order by a.cohort_month, a.months_since_first
