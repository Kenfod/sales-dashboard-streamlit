import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Page Configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("Sales Performance Dashboard")

# --- File Upload Section ---
uploaded_file = st.file_uploader("Upload Sales Data (JSON)", type=["json"])

def clean_currency(value):
    if isinstance(value, str):
        return float(value.replace('$', '').replace(',', ''))
    return float(value)

if uploaded_file is not None:
    # Load Data
    data = json.load(uploaded_file)
    df = pd.DataFrame(data)

    # Data Processing (Equivalent to your JS Logic)
    df['TOTAL SALES'] = df['TOTAL SALES'].apply(clean_currency)
    df['QUANTITY'] = pd.to_numeric(df['QUANTITY'])
    df['ORDER DATE'] = pd.to_datetime(df['ORDER DATE'])

    # --- KPI Section ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sales", f"${df['TOTAL SALES'].sum():,.2f}")
    with col2:
        st.metric("Count of Orders", f"{len(df):,}")
    with col3:
        st.metric("Total Quantity Sold", f"{df['QUANTITY'].sum():,}")

    st.divider()

    # --- Charts Section ---
    
    # 1. Daily Sales Trend
    df_trend = df.groupby('ORDER DATE')['TOTAL SALES'].sum().reset_index().sort_values('ORDER DATE')
    fig_trend = px.line(df_trend, x='ORDER DATE', y='TOTAL SALES', title="Daily Sales", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

    # 2. & 3. Row for Pies
    pie_col1, pie_col2 = st.columns(2)
    
    with pie_col1:
        fig_region = px.pie(df, values='TOTAL SALES', names='REGION', title="Sales by Region")
        st.plotly_chart(fig_region, use_container_width=True)
    
    with pie_col2:
        fig_cat = px.pie(df, values='TOTAL SALES', names='CATEGORY', title="Category Sales")
        st.plotly_chart(fig_cat, use_container_width=True)

    # 4. Salesperson Performance
    df_salesperson = df.groupby('SALESPERSON')['TOTAL SALES'].sum().reset_index()
    fig_sp = px.bar(df_salesperson, x='SALESPERSON', y='TOTAL SALES', title="Salesteam Performance", 
                    color_discrete_sequence=['#28a745'])
    st.plotly_chart(fig_sp, use_container_width=True)

    # 5. Product Sales (Horizontal)
    df_prod = df.groupby('PRODUCT')['TOTAL SALES'].sum().reset_index().sort_values('TOTAL SALES', ascending=True)
    fig_prod = px.bar(df_prod, x='TOTAL SALES', y='PRODUCT', orientation='h', title="Product Sales", 
                      color_discrete_sequence=['#ffc107'])
    st.plotly_chart(fig_prod, use_container_width=True)

else:
    st.info("Please upload a JSON file to see the dashboard.")
    