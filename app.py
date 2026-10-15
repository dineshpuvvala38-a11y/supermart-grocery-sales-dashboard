from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Supermart Grocery Sales Dashboard", page_icon="🛒", layout="wide")
st.title("🛒 Supermart Grocery Sales Dashboard")
st.caption("Interactive analysis of sales, profit, products, discounts and geographic performance")

DATA_PATH = Path(__file__).parent / "data" / "Supermart Grocery Sales - Retail Analytics Dataset.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    for col in ["Category", "Sub Category", "City", "Region", "State", "Customer Name"]:
        df[col] = df[col].astype("string").str.strip()
    for col in ["Sales", "Discount", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df = df.dropna(subset=["Order Date", "Order ID"])
    return df

df = load_data()
min_date, max_date = df["Order Date"].min().date(), df["Order Date"].max().date()

with st.sidebar:
    st.header("Dashboard Filters")
    date_range = st.date_input("Order date range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    categories = st.multiselect("Category", sorted(df["Category"].dropna().unique()),
                                default=sorted(df["Category"].dropna().unique()))
    regions = st.multiselect("Region", sorted(df["Region"].dropna().unique()),
                             default=sorted(df["Region"].dropna().unique()))
    states = st.multiselect("State", sorted(df["State"].dropna().unique()),
                            default=sorted(df["State"].dropna().unique()))

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    df["Order Date"].dt.date.between(start_date, end_date)
    & df["Category"].isin(categories)
    & df["Region"].isin(regions)
    & df["State"].isin(states)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Please adjust the sidebar selections.")
    st.stop()

sales = filtered["Sales"].sum()
profit = filtered["Profit"].sum()
orders = filtered["Order ID"].nunique()
avg_order_sales = sales / orders if orders else 0
margin = profit / sales * 100 if sales else 0

def money(x):
    return f"₹{x:,.0f}"

st.subheader("1. Overall Sales Performance")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Sales", money(sales))
k2.metric("Total Profit", money(profit))
k3.metric("Unique Orders", f"{orders:,}")
k4.metric("Average Sales / Order", money(avg_order_sales))
k5.metric("Profit Margin", f"{margin:.2f}%")

monthly = (filtered.assign(Month=filtered["Order Date"].dt.to_period("M").dt.to_timestamp())
           .groupby("Month", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")))
c1, c2 = st.columns(2)
with c1:
    fig = px.line(monthly, x="Month", y="Sales", markers=True, title="Monthly Sales Trend")
    fig.update_layout(xaxis_title="", yaxis_title="Sales (₹)")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.line(monthly, x="Month", y="Profit", markers=True, title="Monthly Profit Trend")
    fig.update_layout(xaxis_title="", yaxis_title="Profit (₹)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("2. Product Performance")
category_perf = (filtered.groupby("Category", as_index=False)
                 .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
                 .sort_values("Sales", ascending=False))
subcat_perf = (filtered.groupby("Sub Category", as_index=False)
               .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
               .sort_values("Sales", ascending=False))
p1, p2 = st.columns(2)
with p1:
    fig = px.bar(category_perf, x="Category", y="Sales", title="Sales by Category", text_auto=".2s")
    fig.update_layout(xaxis_title="", yaxis_title="Sales (₹)")
    st.plotly_chart(fig, use_container_width=True)
with p2:
    fig = px.bar(category_perf, x="Category", y="Profit", title="Profit by Category", text_auto=".2s")
    fig.update_layout(xaxis_title="", yaxis_title="Profit (₹)")
    st.plotly_chart(fig, use_container_width=True)

fig = px.bar(subcat_perf.head(15).sort_values("Sales"), x="Sales", y="Sub Category",
             orientation="h", title="Top 15 Sub-Categories by Sales", text_auto=".2s")
fig.update_layout(xaxis_title="Sales (₹)", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

product_perf = (filtered.groupby(["Category", "Sub Category"], as_index=False)
                .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")))
product_perf["Profit Margin %"] = product_perf.apply(
    lambda r: r["Profit"] / r["Sales"] * 100 if r["Sales"] else 0, axis=1)
low_profit = product_perf.sort_values(["Sales", "Profit"], ascending=[False, True]).head(10)
st.markdown("**High-sales category/sub-category combinations (inspect profit alongside sales)**")
st.dataframe(low_profit.style.format({"Sales": "₹{:,.2f}", "Profit": "₹{:,.2f}", "Profit Margin %": "{:.2f}%"}),
             use_container_width=True, hide_index=True)

st.divider()
st.subheader("3. Profit and Discount Analysis")
d1, d2 = st.columns(2)
with d1:
    fig = px.scatter(filtered, x="Discount", y="Profit", color="Category",
                     hover_data=["Sub Category", "Sales", "State"],
                     title="Relationship Between Discount and Profit")
    fig.update_layout(xaxis_title="Discount", yaxis_title="Profit (₹)")
    st.plotly_chart(fig, use_container_width=True)
with d2:
    fig = px.bar(category_perf.sort_values("Profit", ascending=False), x="Category", y="Profit",
                 title="Profit by Category", text_auto=".2s")
    fig.update_layout(xaxis_title="", yaxis_title="Profit (₹)")
    st.plotly_chart(fig, use_container_width=True)

discount_bins = pd.cut(filtered["Discount"], bins=5, duplicates="drop")
discount_perf = filtered.assign(Discount_Band=discount_bins.astype(str)).groupby(
    "Discount_Band", as_index=False, observed=False
).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
fig = px.bar(discount_perf, x="Discount_Band", y="Profit", title="Profit by Discount Band", text_auto=".2s")
fig.update_layout(xaxis_title="Discount range", yaxis_title="Profit (₹)")
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("4. Geographic Performance")
geo = (filtered.groupby(["State", "City", "Region"], as_index=False)
       .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
       .sort_values("Sales", ascending=False))
g1, g2 = st.columns(2)
with g1:
    state_sales = geo.groupby("State", as_index=False).agg(Sales=("Sales", "sum")).sort_values("Sales", ascending=False).head(15)
    fig = px.bar(state_sales.sort_values("Sales"), x="Sales", y="State", orientation="h",
                 title="Top 15 States by Sales", text_auto=".2s")
    fig.update_layout(xaxis_title="Sales (₹)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
with g2:
    state_profit = geo.groupby("State", as_index=False).agg(Profit=("Profit", "sum")).sort_values("Profit", ascending=False).head(15)
    fig = px.bar(state_profit.sort_values("Profit"), x="Profit", y="State", orientation="h",
                 title="Top 15 States by Profit", text_auto=".2s")
    fig.update_layout(xaxis_title="Profit (₹)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

city_perf = geo.groupby(["City", "State"], as_index=False).agg(
    Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Orders", "sum"))
city_perf["Profit Margin %"] = city_perf.apply(
    lambda r: r["Profit"] / r["Sales"] * 100 if r["Sales"] else 0, axis=1)
st.markdown("**City-level performance**")
st.dataframe(city_perf.sort_values("Sales", ascending=False).head(25).style.format(
    {"Sales": "₹{:,.2f}", "Profit": "₹{:,.2f}", "Profit Margin %": "{:.2f}%"}),
    use_container_width=True, hide_index=True)

with st.expander("View filtered dataset"):
    st.dataframe(filtered.sort_values("Order Date", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"),
                       file_name="supermart_filtered_sales.csv", mime="text/csv")

st.caption("Source: supplied Supermart Grocery Sales dataset. Educational portfolio project; not affiliated with any retailer.")
