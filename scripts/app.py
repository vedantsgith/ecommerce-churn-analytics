import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="E-commerce Churn Analytics", layout="wide")

@st.cache_data
def load_data():
    rfm = pd.read_csv(os.path.join(BASE_DIR, "..", "data", "processed", "customer_rfm.csv"))
    features = pd.read_csv(os.path.join(BASE_DIR, "..", "data", "processed", "customer_features.csv"))
    rfm = rfm.merge(features, on="customer_unique_id")
    rfm["churned"] = (rfm["recency_days"] > 180).astype(int)
    rfm["avg_order_value"] = rfm["monetary"] / rfm["frequency"]
    rfm["avg_delivery_days"] = rfm["avg_delivery_days"].fillna(rfm["avg_delivery_days"].median())
    return rfm

rfm = load_data()

st.title("E-commerce Customer Churn & Revenue Analytics")

# Top-level metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(rfm):,}")
col2.metric("Churn Rate", f"{rfm['churned'].mean()*100:.1f}%")
col3.metric("Total Revenue", f"${rfm['monetary'].sum():,.0f}")
revenue_at_risk = rfm.loc[rfm['churned'] == 1, 'monetary'].sum()
col4.metric("Revenue at Risk", f"${revenue_at_risk:,.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Customer Segments", "Cohort Retention", "Revenue Trend", "Churn Risk"])

with tab1:
    st.subheader("RFM Customer Segments")

    # Simple segmentation: bucket into quartiles
    rfm["r_score"] = pd.qcut(rfm["recency_days"], 4, labels=[4, 3, 2, 1])  # lower recency = better = higher score
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4])

    def segment_customer(row):
        if row["r_score"] == 4 and row["f_score"] >= 3:
            return "Champions"
        elif row["r_score"] >= 3:
            return "Loyal / Recent"
        elif row["r_score"] == 2:
            return "At Risk"
        else:
            return "Lost"

    rfm["segment"] = rfm.apply(segment_customer, axis=1)

    segment_counts = rfm["segment"].value_counts().reset_index()
    segment_counts.columns = ["Segment", "Customers"]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.bar_chart(segment_counts.set_index("Segment"))
    with col2:
        st.dataframe(segment_counts, use_container_width=True)

    st.scatter_chart(rfm.sample(min(3000, len(rfm))), x="recency_days", y="monetary", color="segment")

import plotly.express as px

with tab2:
    st.subheader("Cohort Retention")

    cohort_df = pd.read_csv(os.path.join(BASE_DIR, "..", "data", "processed", "customer_cohorts.csv"))

    cohort_pivot = cohort_df.pivot_table(
        index="cohort_month", columns="month_number", values="active_customers"
    )

    cohort_size = cohort_pivot[0]
    retention_pct = cohort_pivot.divide(cohort_size, axis=0) * 100

    # Only show first 12 months for readability
    retention_pct = retention_pct.iloc[:, :12]

    fig = px.imshow(
        retention_pct,
        labels=dict(x="Months Since First Purchase", y="Cohort Month", color="Retention %"),
        color_continuous_scale="Blues",
        text_auto=".0f",
        aspect="auto"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Monthly Revenue Trend")

    revenue_df = pd.read_csv(os.path.join(BASE_DIR, "..", "data", "processed", "monthly_revenue.csv"))

    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(revenue_df.set_index("month")["revenue"])
        st.caption("Monthly Revenue")
    with col2:
        st.line_chart(revenue_df.set_index("month")["cumulative_revenue"])
        st.caption("Cumulative Revenue")

    st.dataframe(revenue_df, use_container_width=True)

with tab4:
    st.subheader("Churn Risk")

    import joblib

    model = joblib.load(os.path.join(BASE_DIR, "..", "models", "churn_model.pkl"))

    feature_cols = ["frequency", "monetary", "avg_order_value",
                     "avg_delivery_days", "category_diversity", "avg_installments"]

    rfm["churn_probability"] = model.predict_proba(rfm[feature_cols])[:, 1]

    col1, col2 = st.columns(2)
    col1.metric("Avg Churn Probability", f"{rfm['churn_probability'].mean()*100:.1f}%")
    col2.metric("High-Risk Customers (>70%)", f"{(rfm['churn_probability'] > 0.7).sum():,}")

    st.write("### Top 20 Highest-Risk Customers (by revenue)")
    high_risk = rfm[rfm["churn_probability"] > 0.5].sort_values("monetary", ascending=False).head(20)
    st.dataframe(
        high_risk[["customer_unique_id", "churn_probability", "monetary", "frequency", "avg_delivery_days"]],
        use_container_width=True
    )

    st.write("### What Drives Churn — SHAP Summary")
    st.image(os.path.join(BASE_DIR, "..", "models", "shap_summary.png"), use_container_width=True)