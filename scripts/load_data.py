import pandas as pd
from sqlalchemy import create_engine

# adjust password to match yours
engine = create_engine("mysql+pymysql://root:root1234@localhost/ecommerce")

data_folder = "../data/raw"

# Customers
customers = pd.read_csv(f"{data_folder}/olist_customers_dataset.csv")
customers.to_sql("customers", engine, if_exists="append", index=False)

# Products + category translation merge
products = pd.read_csv(f"{data_folder}/olist_products_dataset.csv")
categories = pd.read_csv(f"{data_folder}/product_category_name_translation.csv")
products = products.merge(categories, on="product_category_name", how="left")
products["product_category_name"] = products["product_category_name"].fillna("unknown")
products["product_category_name_english"] = products["product_category_name_english"].fillna("unknown")
 # drop the 2 incomplete rows
products = products[["product_id", "product_category_name", "product_category_name_english",
                      "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]]
products.to_sql("products", engine, if_exists="append", index=False)

# Orders — parse dates
orders = pd.read_csv(f"{data_folder}/olist_orders_dataset.csv")
date_cols = ["order_purchase_timestamp", "order_approved_at",
             "order_delivered_carrier_date", "order_delivered_customer_date",
             "order_estimated_delivery_date"]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")
orders.to_sql("orders", engine, if_exists="append", index=False)

# Order items
order_items = pd.read_csv(f"{data_folder}/olist_order_items_dataset.csv")
order_items = order_items[["order_id", "order_item_id", "product_id", "price", "freight_value"]]
order_items.to_sql("order_items", engine, if_exists="append", index=False)

# Payments
payments = pd.read_csv(f"{data_folder}/olist_order_payments_dataset.csv")
payments.to_sql("order_payments", engine, if_exists="append", index=False)

print("Done loading all tables.")