# -*- coding: utf-8 -*-
# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set seaborn style
sns.set(style='dark')

# Function to create daily orders dataframe
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        "total_price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)
    return daily_orders_df

# Function to create sum order items dataframe
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_name").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Function to create by-gender dataframe
def create_bygender_df(df):
    bygender_df = df.groupby(by="gender").customer_id.nunique().reset_index()
    bygender_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bygender_df

# Function to create by-age dataframe
def create_byage_df(df):
    byage_df = df.groupby(by="age_group").customer_id.nunique().reset_index()
    byage_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    byage_df['age_group'] = pd.Categorical(byage_df['age_group'], ["Youth", "Adults", "Seniors"])
    return byage_df

# Function to create by-state dataframe
def create_bystate_df(df):
    bystate_df = df.groupby(by="state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df

# Function to create RFM dataframe
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_date": "max",  # Take the most recent order date
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

# Load dataset (Ensure 'all_data.csv' is available in the current directory)
all_df = pd.read_csv("all_data.csv")

# Parse datetime columns
datetime_columns = ["order_date", "delivery_date"]
all_df.sort_values(by="order_date", inplace=True)
all_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Get min and max date
min_date = all_df["order_date"].min()
max_date = all_df["order_date"].max()

# Streamlit sidebar for date input and company logo
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data based on the selected date range
filtered_df = all_df[(all_df['order_date'] >= pd.to_datetime(start_date)) & (all_df['order_date'] <= pd.to_datetime(end_date))]

# Display Daily Orders & Revenue
st.header("Daily Orders and Revenue")
daily_orders_df = create_daily_orders_df(filtered_df)
st.line_chart(daily_orders_df.set_index('order_date')['order_count'], width=0, height=0)
st.line_chart(daily_orders_df.set_index('order_date')['revenue'], width=0, height=0)

# Display Orders by Gender
st.header("Orders by Gender")
bygender_df = create_bygender_df(filtered_df)
st.table(bygender_df)

# Display Orders by Age Group
st.header("Orders by Age Group")
byage_df = create_byage_df(filtered_df)
st.table(byage_df)

# Display Orders by State
st.header("Orders by State")
bystate_df = create_bystate_df(filtered_df)
st.bar_chart(bystate_df.set_index('state')['customer_count'], width=0, height=0)

# RFM Analysis
st.header("RFM Analysis")
rfm_df = create_rfm_df(filtered_df)
st.write(rfm_df)

