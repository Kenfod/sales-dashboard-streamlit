
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Sales Dashboard",
    layout="wide"
)

st.title("Sales Performance Dashboard")

# --------------------------------------------------
# FILE UPLOAD SECTION
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Sales Data (JSON)",
    type=["json"]
)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def clean_currency(value):
    """Convert currency values into numeric values."""

    if pd.isna(value):
        return 0.0

    if isinstance(value, str):
        value = value.strip()
        value = value.replace("$", "").replace(",", "")

        if not value:
            return 0.0

    try:
        return float(value)
    except (ValueError, TypeError):
        return float("nan")


# --------------------------------------------------
# DASHBOARD PROCESSING
# --------------------------------------------------
if uploaded_file is not None:

    try:
        # Load JSON data
        data = json.load(uploaded_file)

        if not isinstance(data, list):
            st.error(
                "Invalid JSON structure. "
                "Expected a list of sales records."
            )
            st.stop()

        if not data:
            st.warning("The uploaded JSON file contains no sales records.")
            st.stop()

        df = pd.DataFrame(data)

        # Normalize column names
        df.columns = (
            df.columns
            .str.strip()
            .str.upper()
        )

        # Rename columns to match dashboard requirements
        df.rename(columns={
            "SALES AMOUNT": "TOTAL SALES",
          }, inplace=True)

        # Required columns
        required_columns = [
            "TOTAL SALES",
            "QUANTITY",
            "ORDER DATE",
            "REGION",
            "CATEGORY",
            "SALESPERSON",
            "PRODUCT"
        ]

        # Validate columns
        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            st.error(
                f"Missing required columns: {missing_columns}"
            )

            st.write(
                "Available columns:",
                df.columns.tolist()
            )

            st.stop()

        # ------------------------------------------
        # DATA CLEANING
        # ------------------------------------------

        df["TOTAL SALES"] = df["TOTAL SALES"].apply(
            clean_currency
        )

        df["TOTAL SALES"] = pd.to_numeric(
            df["TOTAL SALES"],
            errors="coerce"
        )

        df["QUANTITY"] = pd.to_numeric(
            df["QUANTITY"],
            errors="coerce"
        )

        df["ORDER DATE"] = pd.to_datetime(
            df["ORDER DATE"],
            errors="coerce"
        )

        # Remove records with invalid essential values
        df = df.dropna(
            subset=[
                "TOTAL SALES",
                "QUANTITY",
                "ORDER DATE"
            ]
        )

        if df.empty:
            st.error("No valid sales records remain after data cleaning.")
            st.stop()

        # ------------------------------------------
        # KPI SECTION
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Sales",
                f"${df['TOTAL SALES'].sum():,.2f}"
            )

        with col2:
            st.metric(
                "Count of Orders",
                f"{len(df):,}"
            )

        with col3:
            st.metric(
                "Total Quantity Sold",
                f"{df['QUANTITY'].sum():,.0f}"
            )

        st.divider()

        # ------------------------------------------
        # CHART 1: DAILY SALES TREND
        # ------------------------------------------

        df["ORDER DATE"] = df["ORDER DATE"].dt.normalize()

        df_trend = (
            df.groupby("ORDER DATE")["TOTAL SALES"]
            .sum()
            .reset_index()
            .sort_values("ORDER DATE")
        )

        fig_trend = px.line(
            df_trend,
            x="ORDER DATE",
            y="TOTAL SALES",
            title="Daily Sales",
            markers=True
        )

        st.plotly_chart(
            fig_trend,
            width="stretch"
        )

        # ------------------------------------------
        # CHARTS 2 & 3: SALES BREAKDOWN
        # ------------------------------------------

        pie_col1, pie_col2 = st.columns(2)

        with pie_col1:

            fig_region = px.pie(
                df,
                values="TOTAL SALES",
                names="REGION",
                title="Sales by Region"
            )

            st.plotly_chart(
                fig_region,
                width="stretch"
            )

        with pie_col2:

            fig_cat = px.pie(
                df,
                values="TOTAL SALES",
                names="CATEGORY",
                title="Category Sales"
            )

            st.plotly_chart(
                fig_cat,
                width="stretch"
            )

        # ------------------------------------------
        # CHART 4: SALESPERSON PERFORMANCE
        # ------------------------------------------

        df_salesperson = (
            df.groupby("SALESPERSON")["TOTAL SALES"]
            .sum()
            .reset_index()
            .sort_values("TOTAL SALES", ascending=False)
        )

        fig_sp = px.bar(
            df_salesperson,
            x="SALESPERSON",
            y="TOTAL SALES",
            title="Salesperson Performance",
            color_discrete_sequence=["#28a745"]
        )

        st.plotly_chart(
            fig_sp,
            width="stretch"
        )

        # ------------------------------------------
        # CHART 5: PRODUCT SALES
        # ------------------------------------------

        df_prod = (
            df.groupby("PRODUCT")["TOTAL SALES"]
            .sum()
            .reset_index()
            .sort_values("TOTAL SALES", ascending=True)
        )

        fig_prod = px.bar(
            df_prod,
            x="TOTAL SALES",
            y="PRODUCT",
            orientation="h",
            title="Product Sales",
            color_discrete_sequence=["#ffc107"]
        )

        st.plotly_chart(
            fig_prod,
            width="stretch"
        )

        # ------------------------------------------
        # RAW DATA PREVIEW
        # ------------------------------------------

        with st.expander("View Sales Data"):

            st.dataframe(
                df,
                width="stretch"
            )

    except json.JSONDecodeError:
        st.error("The uploaded file is not valid JSON.")

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

else:

    st.info("Please upload a JSON file to see the dashboard.")
