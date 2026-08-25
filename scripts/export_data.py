import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:root1234@localhost/ecommerce")

views = {
    "customer_rfm": "SELECT * FROM customer_rfm",
    "customer_features": "SELECT * FROM customer_features",
    "customer_cohorts": "SELECT * FROM customer_cohorts",
    "monthly_revenue": "SELECT * FROM monthly_revenue"
}

for name, query in views.items():
    df = pd.read_sql(query, engine)
    df.to_csv(f"../data/processed/{name}.csv", index=False)
    print(f"Exported {name}: {df.shape}")