select
    p.product_id,
    p.product_category_name                                      as category_pt,
    coalesce(t.product_category_name_english,
             p.product_category_name, 'unknown')                 as category,
    p.product_photos_qty                                         as photos_qty,
    p.product_weight_g                                           as weight_g,
    p.product_length_cm * p.product_height_cm * p.product_width_cm as volume_cm3
from {{ source('olist', 'olist_products_dataset') }} p
left join {{ source('olist', 'product_category_name_translation') }} t
    on p.product_category_name = t.product_category_name
