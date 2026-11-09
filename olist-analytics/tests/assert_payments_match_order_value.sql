-- Paid amount should match items + freight (allowing for vouchers/rounding) for 99%+ of orders.
with diffs as (
    select abs(payment_value - gross_revenue) > 1 as mismatch
    from {{ ref('fact_orders') }}
    where payment_value is not null and items_count > 0
)
select count_if(mismatch) * 1.0 / count(*) as mismatch_rate
from diffs
having count_if(mismatch) * 1.0 / count(*) > 0.01
