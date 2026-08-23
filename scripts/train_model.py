import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib
from sklearn.utils.class_weight import compute_sample_weight
engine = create_engine("mysql+pymysql://root:root1234@localhost/ecommerce")

# Join RFM with the new features
rfm = pd.read_sql("""
    SELECT r.*, f.avg_delivery_days, f.category_diversity, f.avg_installments
    FROM customer_rfm r
    JOIN customer_features f ON r.customer_unique_id = f.customer_unique_id
""", engine)

rfm["churned"] = (rfm["recency_days"] > 180).astype(int)
rfm["avg_order_value"] = rfm["monetary"] / rfm["frequency"]

# Handle any missing delivery days (fill with median)
rfm["avg_delivery_days"] = rfm["avg_delivery_days"].fillna(rfm["avg_delivery_days"].median())

feature_cols = ["frequency", "monetary", "avg_order_value",
                 "avg_delivery_days", "category_diversity", "avg_installments"]

X = rfm[feature_cols]
y = rfm["churned"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

model = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.1,
    eval_metric="logloss"
)
model.fit(X_train, y_train, sample_weight=sample_weights)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print("ROC AUC:", roc_auc_score(y_test, y_proba))

joblib.dump(model, "../models/churn_model.pkl")
print("Model saved.")