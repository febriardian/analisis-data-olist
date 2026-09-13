import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 1. SET UP HALAMAN & TEMA
st.set_page_config(page_title="E-Commerce Analytics", layout="wide")
sns.set(style="dark")
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# 2. HELPER FUNCTIONS
def create_product_df(df):
    product_df = df.groupby("product_category_name")["price"].sum().reset_index()
    product_df = product_df.sort_values(by="price", ascending=False).head(5)
    return product_df

def create_time_pivot(df):
    if 'order_day' not in df.columns:
        df['order_day'] = df['order_purchase_timestamp'].dt.day_name()
    if 'order_hour' not in df.columns:
        df['order_hour'] = df['order_purchase_timestamp'].dt.hour()
    time_pivot = df.groupby(['order_day', 'order_hour']) ['order_id'].nunique().unstack()
    time_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    time_pivot = time_pivot.reindex(time_days)
    return time_pivot

def create_payment_df(df):
    payment_df = df.groupby('payment_type')['order_id'].nunique().sort_values(ascending=False)
    return payment_df

def create_demographic_df(df):
    # Demografi berdasarkan pendapatan
    revenue_state = df.groupby('customer_state')['price'].sum().reset_index()
    revenue_state = revenue_state.sort_values(by='price', ascending=False).head(5)
    # Demografi berdasarkan jumlah pelanggan
    customer_state = df.groupby('customer_state')['customer_unique_id'].nunique().reset_index()
    customer_state = customer_state.sort_values(by='customer_unique_id', ascending=False).head(5)
    return revenue_state, customer_state

def create_rfm_df(df):
    snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()
    rfm_df.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']
    return rfm_df

# 3. LOAD DATA
def load_data():
    df = pd.read_csv("Dashboard/main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    df_2017 = df[df['order_purchase_timestamp'].dt.year == 2017]
    return df_2017

all_df = load_data()

# 4. UI DASHBOARD
st.title("E-Commerce Performance Dashboard (2017)")
st.markdown("---")

total_revenue = all_df['price'].sum()
total_orders = all_df['order_id'].nunique()
total_customers = all_df['customer_unique_id'].nunique()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
with col2:
    st.metric("Total Orders", f"{total_orders:,}")
with col3:
    st.metric("Total Customers", f"{total_customers:,}")

st.markdown("---")

# BAGIAN 1: PERFORMA PRODUK
st.subheader("1. Kategori Produk Berpendapatan Tertinggi")
product_df = create_product_df(all_df)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="price", y="product_category_name", data=product_df, palette=colors, ax=ax)
ax.set_title("Top 5 Kategori Produk Berdasarkan Total Pendapatan ", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel(None)
ax.set_ylabel(None)

st.pyplot(fig)
st.markdown("---")

# BAGIAN 2: POLA TRANSAKSI & PEMBAYARAN
st.subheader("2. Pola Waktu Transaksi & Metode Pembayaran")

# GRAFIK 1: HEATMAP POLA TRANSAKSI
st.markdown("**2.1 Kepadatan Transaki**")
time_pivot = create_time_pivot(all_df)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(time_pivot, cmap="Blues", linewidths=.5, ax=ax)
ax.set_xlabel(None)
ax.set_ylabel(None)

st.pyplot(fig)

# GRAFIK 2: BAR CHART METODE PEMBAYARAN
st.markdown("**2.2 Metode Pembayaran Paling Populer**")
payment_df = create_payment_df(all_df)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=payment_df.values, y=payment_df.index, palette=colors, ax=ax)
ax.set_xlabel(None)
ax.set_ylabel(None)

st.pyplot(fig)
st.markdown("---")

# BAGIAN 3: DEMOGRAFI PELANGGAN
st.subheader("3. Peta Kekuatan Pasar (Top 5 Negara Bagian)")
revenue_state, customer_state = create_demographic_df(all_df)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))

# KOTAK KIRI: GRAFIK TOTAL PENDAPATAN
sns.barplot(x='price', y='customer_state', data=revenue_state, palette=colors, ax=ax[0])
ax[0].set_title("Berdasarkan Total Pendapatan", fontsize=15, fontweight="bold", pad=15)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)

# KOTAK KANAN: GRAFIK JUMLAH PELANGGAN
sns.barplot(x='customer_unique_id', y='customer_state', data=customer_state, palette=colors, ax=ax[1])
ax[1].set_title("Berdasarkan Jumlah Pelanggan", fontsize=15, fontweight="bold", pad=15)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)

st.pyplot(fig)
st.markdown("---")

# BAGIAN 4: RFM ANALYSIS
st.subheader("4. RFM Analysis")
rfm_df = create_rfm_df(all_df)

top_recency = rfm_df.sort_values(by='Recency', ascending=True).head(5)
top_frequency = rfm_df.sort_values(by='Frequency', ascending=False).head(5)
top_monetary = rfm_df.sort_values(by='Monetary', ascending=False).head(5)

top_recency['short_id'] = top_recency['customer_unique_id'].str[:8]
top_frequency['short_id'] = top_frequency['customer_unique_id'].str[:8]
top_monetary['short_id'] = top_monetary['customer_unique_id'].str[:8]

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

# Plot 1: Recency
sns.barplot(x='short_id', y='Recency', data=top_recency, color="#72BCD4", ax=ax[0])
ax[0].set_title("By Recency (days)", fontsize=14, fontweight="bold", pad=15)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)

# Plot 2: Frequency
sns.barplot(x='short_id', y='Frequency', data=top_frequency, color="#72BCD4", ax=ax[1])
ax[1].set_title("By Frequency", fontsize=14, fontweight="bold", pad=15)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)

# Plot 3: Monetary
sns.barplot(x='short_id', y='Monetary', data=top_monetary, color="#72BCD4", ax=ax[2])
ax[2].set_title("By Monetary", fontsize=14, fontweight="bold", pad=15)
ax[2].set_xlabel(None)
ax[2].set_ylabel(None)

plt.tight_layout()
st.pyplot(fig)
st.markdown("""
    <hr style="border:1px solid #e6e6e6; margin-top: 10px; margin-bottom: 10px;">
    <div style="text-align: center; color: #888888; padding-bottom: 20px;">
        <p style="font-size: 16px; margin-bottom: 5px; font-weight: bold;">
            E-Commerce Data Analysis Project
        </p>
        <p style="font-size: 12px; margin-bottom: 5px;">
            Created by: <b>Febri Nur Ardian Syah</b> | Dicoding Academy
        </p>
        <p style="font-size: 11px;">
            © September 2026. All Rights Reserved.
        </p>
    </div>
""", unsafe_allow_html=True)
