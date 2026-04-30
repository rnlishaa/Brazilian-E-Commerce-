import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import json
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import warnings
warnings.filterwarnings('ignore')

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ===== COLOR PALETTE =====
COLOR_PRIMARY   = '#DB1A1A'
COLOR_SECONDARY = '#FF7070'
COLOR_PASTEL    = '#FFA6A6'
COLOR_CREAM     = '#FFF6F6'
COLOR_TEAL      = '#8CC7C4'
COLOR_TEAL_DARK = '#2C687B'
COLOR_ACCENT    = '#FFEDC7'

SEGMENT_COLORS = {
    'Champions'          : COLOR_PRIMARY,
    'Loyal Customers'    : COLOR_SECONDARY,
    'New Customers'      : COLOR_PASTEL,
    'At Risk'            : COLOR_TEAL,
    'Lost Customers'     : COLOR_TEAL_DARK,
    'Potential Loyalists': COLOR_ACCENT
}

STATE_NAMES = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AM': 'Amazonas', 'AP': 'Amapá',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
    'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
    'MG': 'Minas Gerais', 'MS': 'Mato Grosso do Sul', 'MT': 'Mato Grosso',
    'PA': 'Pará', 'PB': 'Paraíba', 'PE': 'Pernambuco', 'PI': 'Piauí',
    'PR': 'Paraná', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RO': 'Rondônia', 'RR': 'Roraima', 'RS': 'Rio Grande do Sul',
    'SC': 'Santa Catarina', 'SE': 'Sergipe', 'SP': 'São Paulo',
    'TO': 'Tocantins',
}

def get_state_name(code):
    return STATE_NAMES.get(code, code)

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    main = pd.read_csv('dashboard/main_data.csv',
                        parse_dates=['order_purchase_timestamp'])
    rfm  = pd.read_csv('dashboard/rfm_data.csv')
    geo  = pd.read_csv('dashboard/customers_geo.csv')
    return main, rfm, geo

main_data, rfm_data, customers_geo = load_data()

# ===== CUSTOM CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.main { background-color: #FFFFFF; }
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #DB1A1A 0%, #991212 50%, #2C687B 100%) !important;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label {
    color: rgba(255,255,255,0.8) !important;
    font-size: 12px !important;
    font-style: italic;
}
.metric-card {
    background-color: #FFF6F6;
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #DB1A1A;
    margin-bottom: 10px;
}
.metric-card-teal {
    background-color: #F0F8F8;
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #2C687B;
    margin-bottom: 10px;
}
.metric-title { font-size: 12px; color: #999; margin-bottom: 4px; font-style: italic; }
.metric-value { font-size: 22px; font-weight: 600; color: #DB1A1A; }
.metric-value-teal { font-size: 22px; font-weight: 600; color: #2C687B; }
.metric-delta { font-size: 11px; color: #2C687B; margin-top: 3px; }
h1 { color: #DB1A1A !important; font-weight: 600 !important; letter-spacing: -0.5px !important; }
h2, h3 { color: #DB1A1A !important; }
.section-divider { border: none; border-top: 1.5px solid #FFA6A6; margin: 2rem 0; opacity: 0.5; }
.filter-inline-label { font-size: 12px; color: #999; font-style: italic; margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: #999; font-style: italic; margin-top: -12px; margin-bottom: 20px; }
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #FFF6F6;
    padding: 8px 12px;
    border-radius: 12px;
    margin-bottom: 20px;
}
.stTabs [data-baseweb="tab"] {
    background-color: white;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #888 !important;
    border: 0.5px solid #eee;
}
.stTabs [aria-selected="true"] {
    background-color: #DB1A1A !important;
    color: white !important;
    border-color: #DB1A1A !important;
}
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
st.sidebar.title("🛒 Olist Dashboard")
st.sidebar.markdown("<p style='font-size:11px; font-style:italic; color:rgba(255,255,255,0.6); margin-top:-10px;'>E-Commerce Analytics 2016–2018</p>",
                    unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("📅 Filter Periode")
min_date = main_data['order_purchase_timestamp'].min().date()
max_date = main_data['order_purchase_timestamp'].max().date()
start_date = st.sidebar.date_input("Tanggal Mulai", min_date,
                                    min_value=min_date, max_value=max_date)
end_date   = st.sidebar.date_input("Tanggal Akhir", max_date,
                                    min_value=min_date, max_value=max_date)

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Filter Provinsi")
all_states_codes   = sorted(main_data['customer_state'].dropna().unique().tolist())
all_states_display = {get_state_name(c): c for c in all_states_codes}
state_options      = ["Semua Provinsi"] + sorted(all_states_display.keys())
selected_state_name = st.sidebar.selectbox("Pilih Provinsi", options=state_options)
selected_state      = all_states_display.get(selected_state_name, None)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size:11px; color:rgba(255,255,255,0.6);'><i>Dataset: Brazilian E-Commerce<br>Sumber: Olist / Kaggle</i></p>",
                    unsafe_allow_html=True)

# ===== APPLY FILTER =====
filtered = main_data[
    (main_data['order_purchase_timestamp'].dt.date >= start_date) &
    (main_data['order_purchase_timestamp'].dt.date <= end_date)
].copy()
if selected_state_name != "Semua Provinsi" and selected_state:
    filtered = filtered[filtered['customer_state'] == selected_state]

# ===== HEADER =====
st.title("🛒 Brazilian E-Commerce Dashboard")
st.markdown("<p class='page-subtitle'>Analisis data transaksi Olist — periode 2016 hingga 2018</p>",
            unsafe_allow_html=True)
if selected_state_name != "Semua Provinsi":
    st.info(f"Menampilkan data untuk provinsi: **{selected_state_name}**")

# ===== METRIC CARDS =====
total_revenue   = filtered['payment_value'].sum()
total_orders    = filtered['order_id'].nunique()
total_customers = filtered['customer_id'].nunique()
avg_review      = filtered['review_score'].mean() if 'review_score' in filtered.columns else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value">R${total_revenue:,.0f}</div>
        <div class="metric-delta">▲ trend naik 2016–2018</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Total Order</div>
        <div class="metric-value">{total_orders:,}</div>
        <div class="metric-delta">Nov 2017 puncak tertinggi</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">Total Pelanggan</div>
        <div class="metric-value">{total_customers:,}</div>
        <div class="metric-delta">dari {filtered['customer_state'].nunique()} provinsi</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card-teal">
        <div class="metric-title">Rata-rata Review Score</div>
        <div class="metric-value-teal">{avg_review:.2f} ★</div>
        <div class="metric-delta" style="color:#DB1A1A;">kepuasan pelanggan tinggi</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ===== TABS =====
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tren Revenue & Order",
    "📦 Kategori Produk",
    "👥 RFM Analysis",
    "⭐ Review & Delivery",
    "🗺️ Geospatial & Clustering"
])

# ==================== TAB 1 ====================
with tab1:
    st.subheader("📈 Tren Revenue & Order Bulanan")
    st.markdown("<p class='filter-inline-label'>Tren keseluruhan berdasarkan filter periode dan provinsi yang dipilih</p>",
                unsafe_allow_html=True)

    filtered['year_month'] = filtered['order_purchase_timestamp'].dt.to_period('M')
    monthly_rev = filtered.groupby('year_month')['payment_value'].sum().reset_index()
    monthly_ord = filtered.groupby('year_month')['order_id'].nunique().reset_index()
    monthly_rev['year_month'] = monthly_rev['year_month'].astype(str)
    monthly_ord['year_month'] = monthly_ord['year_month'].astype(str)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('white')
        ax.set_facecolor(COLOR_CREAM)
        ax.plot(range(len(monthly_rev)), monthly_rev['payment_value'],
                marker='o', color=COLOR_PRIMARY, linewidth=2.5,
                markerfacecolor='white', markeredgecolor=COLOR_PRIMARY, markeredgewidth=2)
        ax.fill_between(range(len(monthly_rev)), monthly_rev['payment_value'],
                        alpha=0.15, color=COLOR_PRIMARY)
        if len(monthly_rev) > 0:
            max_idx = monthly_rev['payment_value'].idxmax()
            ax.annotate(f"Tertinggi\n{monthly_rev.loc[max_idx,'year_month']}",
                        xy=(max_idx, monthly_rev.loc[max_idx,'payment_value']),
                        xytext=(-40, 10), textcoords='offset points',
                        fontsize=8, color=COLOR_PRIMARY, fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=COLOR_PRIMARY, lw=1.2))
        ax.set_title('Total Revenue Bulanan', fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(monthly_rev)))
        ax.set_xticklabels(monthly_rev['year_month'], rotation=45, ha='right', fontsize=7)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R${x:,.0f}'))
        ax.grid(axis='y', alpha=0.3, color=COLOR_PASTEL)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('white')
        ax.set_facecolor(COLOR_CREAM)
        bar_colors = [COLOR_PRIMARY if v == monthly_ord['order_id'].max()
                      else COLOR_TEAL for v in monthly_ord['order_id']]
        ax.bar(range(len(monthly_ord)), monthly_ord['order_id'],
               color=bar_colors, edgecolor='white', linewidth=0.6)
        if len(monthly_ord) > 0:
            max_idx_ord = monthly_ord['order_id'].idxmax()
            ax.annotate(monthly_ord.loc[max_idx_ord, 'year_month'],
                        xy=(max_idx_ord, monthly_ord.loc[max_idx_ord, 'order_id']),
                        xytext=(0, 6), textcoords='offset points',
                        ha='center', fontsize=7, color=COLOR_PRIMARY, fontweight='bold')
        ax.set_title('Tren Order Bulanan', fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(monthly_ord)))
        ax.set_xticklabels(monthly_ord['year_month'], rotation=45, ha='right', fontsize=7)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        ax.set_ylabel('Jumlah Order', fontsize=9)
        ax.grid(axis='y', alpha=0.3, color=COLOR_PASTEL)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    if len(monthly_rev) > 0:
        max_rev_month = monthly_rev.loc[monthly_rev['payment_value'].idxmax(), 'year_month']
        max_rev_val   = monthly_rev['payment_value'].max()
        st.info(f"💡 **Insight:** Revenue tertinggi terjadi pada **{max_rev_month}** sebesar **R${max_rev_val:,.0f}** — kemungkinan dipicu event Black Friday / Harbolnas.")

# ==================== TAB 2 ====================
with tab2:
    st.subheader("📦 Analisis Kategori Produk")

    all_categories = sorted(filtered['product_category_name_english'].dropna().unique().tolist())
    col_f, _ = st.columns([2, 3])
    with col_f:
        st.markdown("<p class='filter-inline-label'>Filter Kategori:</p>", unsafe_allow_html=True)
        selected_category = st.selectbox("", options=["Semua Kategori"] + all_categories,
                                          key="cat_filter", label_visibility="collapsed")

    if selected_category == "Semua Kategori":
        top_cat = filtered['product_category_name_english'].value_counts().head(5).reset_index()
        top_cat.columns = ['Category', 'Count']
        rev_cat = (filtered.groupby('product_category_name_english')['payment_value']
                   .sum().sort_values(ascending=False).head(10).reset_index())
        rev_cat.columns = ['Category', 'Revenue']

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('white')
            ax.set_facecolor(COLOR_CREAM)
            colors_cat = [COLOR_PRIMARY if i == 0 else COLOR_TEAL for i in range(len(top_cat))]
            bars = ax.barh(top_cat['Category'], top_cat['Count'],
                           color=colors_cat, edgecolor='white')
            for bar, val in zip(bars, top_cat['Count']):
                ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                        f'{val:,}', va='center', fontsize=9,
                        color=COLOR_TEAL_DARK, fontweight='bold')
            ax.set_title('Top 5 Kategori Produk Terlaris', fontsize=12, fontweight='bold')
            ax.grid(axis='x', alpha=0.3, color=COLOR_PASTEL)
            ax.spines[['top','right']].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('white')
            ax.set_facecolor(COLOR_CREAM)
            rev_sorted = rev_cat.sort_values('Revenue', ascending=True)
            colors_rev = [COLOR_PRIMARY if i == len(rev_sorted)-1 else COLOR_TEAL
                          for i in range(len(rev_sorted))]
            bars = ax.barh(rev_sorted['Category'], rev_sorted['Revenue'],
                           color=colors_rev, edgecolor='white')
            for bar, val in zip(bars, rev_sorted['Revenue']):
                ax.text(bar.get_width() + rev_sorted['Revenue'].max()*0.01,
                        bar.get_y() + bar.get_height()/2,
                        f'R${val:,.0f}', va='center', fontsize=8,
                        color=COLOR_TEAL_DARK, fontweight='bold')
            ax.set_title('Top 10 Kategori — Total Revenue', fontsize=12, fontweight='bold')
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R${x/1e6:.1f}M'))
            ax.grid(axis='x', alpha=0.3, color=COLOR_PASTEL)
            ax.spines[['top','right']].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        top_category    = top_cat.iloc[0]['Category']
        top_revenue_cat = rev_cat.iloc[0]['Category']
        st.info(f"💡 **Insight:** Kategori paling laku: **{top_category}** | Revenue terbesar: **{top_revenue_cat}**")

    else:
        filtered_cat = filtered[
            filtered['product_category_name_english'] == selected_category].copy()

        cat_orders  = filtered_cat['order_id'].nunique()
        cat_revenue = filtered_cat['payment_value'].sum()
        cat_avg     = filtered_cat['payment_value'].mean()
        total_rev   = filtered['payment_value'].sum()
        cat_pct     = (cat_revenue / total_rev * 100) if total_rev > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Total Order</div>
                <div class="metric-value">{cat_orders:,}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Total Revenue</div>
                <div class="metric-value">R${cat_revenue:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card-teal">
                <div class="metric-title">Rata-rata per Order</div>
                <div class="metric-value-teal">R${cat_avg:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="metric-card-teal">
                <div class="metric-title">% dari Total Revenue</div>
                <div class="metric-value-teal">{cat_pct:.1f}%</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            filtered_cat['year_month'] = filtered_cat['order_purchase_timestamp'].dt.to_period('M')
            cat_monthly = filtered_cat.groupby('year_month')['payment_value'].sum().reset_index()
            cat_monthly['year_month'] = cat_monthly['year_month'].astype(str)

            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('white')
            ax.set_facecolor(COLOR_CREAM)
            ax.plot(range(len(cat_monthly)), cat_monthly['payment_value'],
                    marker='o', color=COLOR_PRIMARY, linewidth=2.5,
                    markerfacecolor='white', markeredgecolor=COLOR_PRIMARY, markeredgewidth=2)
            ax.fill_between(range(len(cat_monthly)), cat_monthly['payment_value'],
                            alpha=0.15, color=COLOR_PRIMARY)
            ax.set_title(f'Tren Revenue Bulanan — {selected_category}',
                         fontsize=12, fontweight='bold')
            ax.set_xticks(range(len(cat_monthly)))
            ax.set_xticklabels(cat_monthly['year_month'], rotation=45, ha='right', fontsize=7)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R${x:,.0f}'))
            ax.grid(axis='y', alpha=0.3, color=COLOR_PASTEL)
            ax.spines[['top','right']].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            cat_review     = filtered_cat['review_score'].value_counts().sort_index()
            cat_rev_pct    = (cat_review / cat_review.sum() * 100).round(1)
            cat_avg_review = filtered_cat['review_score'].mean()
            review_bar_colors = [COLOR_TEAL_DARK, COLOR_TEAL, COLOR_PASTEL,
                                 COLOR_SECONDARY, COLOR_PRIMARY]

            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('white')
            ax.set_facecolor(COLOR_CREAM)
            bars = ax.bar(cat_review.index.astype(str), cat_review.values,
                          color=review_bar_colors[:len(cat_review)],
                          edgecolor='white', linewidth=1.5)
            for bar, val, pct in zip(bars, cat_review.values, cat_rev_pct.values):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + cat_review.values.max()*0.01,
                        f'{val:,}\n({pct}%)', ha='center', va='bottom',
                        fontsize=8, color=COLOR_TEAL_DARK, fontweight='bold')
            ax.set_xlabel('Review Score (bintang)', fontsize=9)
            ax.set_ylabel('Jumlah Ulasan', fontsize=9)
            ax.set_title(f'Review Score — {selected_category}\n★ Rata-rata {cat_avg_review:.2f}',
                         fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, color=COLOR_PASTEL)
            ax.spines[['top','right']].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        st.info(f"💡 **Insight:** Kategori **{selected_category}** menyumbang **{cat_pct:.1f}%** dari total revenue dengan rata-rata order value **R${cat_avg:,.0f}**.")

# ==================== TAB 3 ====================
with tab3:
    st.subheader("👥 RFM Analysis — Segmentasi Pelanggan")

    all_segments = sorted(rfm_data['Segment'].unique().tolist())
    col_f2, _ = st.columns([2, 3])
    with col_f2:
        st.markdown("<p class='filter-inline-label'>Filter Segmen:</p>", unsafe_allow_html=True)
        selected_segment = st.selectbox("", options=["Semua Segmen"] + all_segments,
                                         key="seg_filter", label_visibility="collapsed")

    rfm_filtered = rfm_data.copy()
    if selected_segment != "Semua Segmen":
        rfm_filtered = rfm_filtered[rfm_filtered['Segment'] == selected_segment]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Total Pelanggan (Segmen)</div>
            <div class="metric-value">{len(rfm_filtered):,}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Rata-rata Recency (hari)</div>
            <div class="metric-value">{rfm_filtered['Recency'].mean():,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card-teal">
            <div class="metric-title">Rata-rata Monetary</div>
            <div class="metric-value-teal">R${rfm_filtered['Monetary'].mean():,.0f}</div>
        </div>""", unsafe_allow_html=True)

    seg_counts  = rfm_data['Segment'].value_counts().reset_index()
    seg_counts.columns = ['Segment', 'Count']
    rfm_summary = rfm_data.groupby('Segment')['Monetary'].mean().reset_index()
    rfm_summary.columns = ['Segment', 'Avg_Monetary']
    rfm_summary = rfm_summary.sort_values('Avg_Monetary', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor('white')
        ax.set_facecolor(COLOR_CREAM)
        seg_sorted = seg_counts.sort_values('Count', ascending=True)
        colors_seg_bar = [SEGMENT_COLORS.get(s, COLOR_TEAL) for s in seg_sorted['Segment']]
        bars = ax.barh(seg_sorted['Segment'], seg_sorted['Count'],
                       color=colors_seg_bar, edgecolor='white')
        for bar, val in zip(bars, seg_sorted['Count']):
            ax.text(bar.get_width() + seg_sorted['Count'].max()*0.01,
                    bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=9,
                    color=COLOR_TEAL_DARK, fontweight='bold')
        ax.set_title('Distribusi Segmen Pelanggan', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, color=COLOR_PASTEL)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        rfm_radar = rfm_data.groupby('Segment').agg(
            Recency=('Recency','mean'),
            Frequency=('Frequency','mean'),
            Monetary=('Monetary','mean')
        ).reset_index()
        for col in ['Recency','Frequency','Monetary']:
            rfm_radar[col+'_n'] = (rfm_radar[col] - rfm_radar[col].min()) / \
                                   (rfm_radar[col].max() - rfm_radar[col].min() + 1e-9)
        rfm_radar['Recency_n'] = 1 - rfm_radar['Recency_n']

        categories = ['Recency\n(lebih baru)', 'Frequency\n(lebih sering)', 'Monetary\n(lebih besar)']
        N      = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(7, 5), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('#F8F8F8')
        legend_handles = []
        for i, row in rfm_radar.iterrows():
            vals  = [row['Recency_n'], row['Frequency_n'], row['Monetary_n']]
            vals += vals[:1]
            color = SEGMENT_COLORS.get(row['Segment'], COLOR_TEAL)
            ax.plot(angles, vals, color=color, linewidth=1.8)
            ax.fill(angles, vals, color=color, alpha=0.08)
            legend_handles.append(mpatches.Patch(color=color, label=row['Segment']))
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=8, color=COLOR_TEAL_DARK)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(['25%','50%','75%','100%'], fontsize=6, color='#aaa')
        ax.set_ylim(0, 1)
        ax.spines['polar'].set_color('#ddd')
        ax.grid(color='#ddd', alpha=0.5)
        ax.set_title('Profil RFM per Segmen (Radar)', fontsize=12, fontweight='bold', pad=18)
        ax.legend(handles=legend_handles, loc='lower center',
                  bbox_to_anchor=(0.5, -0.28), ncol=3, fontsize=7, frameon=False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("<p class='filter-inline-label' style='margin-top:1rem;'>Customer Segmentation — Bubble Chart</p>",
                unsafe_allow_html=True)
    rfm_avg = rfm_data.groupby('Segment').agg(
        Recency=('Recency','mean'),
        Frequency=('Frequency','mean'),
        Monetary=('Monetary','mean')
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor(COLOR_CREAM)
    for _, row in rfm_avg.iterrows():
        ax.scatter(row['Frequency'], row['Monetary'],
                   s=row['Recency']*2,
                   color=SEGMENT_COLORS.get(row['Segment'], COLOR_TEAL),
                   alpha=0.7, edgecolors='white', linewidth=1.5)
        ax.text(row['Frequency'], row['Monetary']+3, row['Segment'],
                fontsize=8, ha='center', color=COLOR_TEAL_DARK, fontweight='bold')
    ax.set_xlabel('Frequency (rata-rata transaksi)', fontsize=9)
    ax.set_ylabel('Monetary (rata-rata belanja)', fontsize=9)
    ax.set_title('Segmentasi Pelanggan — Bubble Chart\n(ukuran bubble = Recency)',
                 fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3, color=COLOR_PASTEL)
    ax.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info("💡 **Insight:** Segmen **At Risk** mendominasi dengan 22.229 pelanggan. Segmen **Champions** memiliki monetary tertinggi namun jumlahnya lebih sedikit.")

# ==================== TAB 4 ====================
with tab4:
    st.subheader("⭐ Review & Delivery Analysis")

    avg_days      = filtered['actual_delivery_days'].mean()
    late_orders   = (filtered['delivery_diff_days'] > 0).sum()
    ontime_orders = (filtered['delivery_diff_days'] <= 0).sum()
    total_del     = late_orders + ontime_orders
    ontime_pct    = (ontime_orders / total_del * 100) if total_del > 0 else 0
    late_pct      = (late_orders   / total_del * 100) if total_del > 0 else 0

    m1, m2, m3, _ = st.columns([1, 1, 1, 3])
    with m1:
        st.markdown(f"""<div class="metric-card-teal">
            <div class="metric-title">Rata-rata Pengiriman</div>
            <div class="metric-value-teal">{avg_days:.1f} hari</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card-teal">
            <div class="metric-title">Tepat / Lebih Cepat</div>
            <div class="metric-value-teal">{ontime_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Terlambat</div>
            <div class="metric-value">{late_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        review_counts     = filtered['review_score'].value_counts().sort_index()
        review_pct        = (review_counts / review_counts.sum() * 100).round(1)
        review_bar_colors = [COLOR_TEAL_DARK, COLOR_TEAL, COLOR_PASTEL,
                             COLOR_SECONDARY, COLOR_PRIMARY]
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor('white')
        ax.set_facecolor(COLOR_CREAM)
        bars = ax.bar(review_counts.index.astype(str), review_counts.values,
                      color=review_bar_colors, edgecolor='white', linewidth=1.5)
        for bar, val, pct in zip(bars, review_counts.values, review_pct.values):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + review_counts.values.max()*0.01,
                    f'{val:,}\n({pct}%)', ha='center', va='bottom',
                    fontsize=8, color=COLOR_TEAL_DARK, fontweight='bold')
        ax.set_xlabel('Review Score (bintang)', fontsize=9)
        ax.set_ylabel('Jumlah Ulasan', fontsize=9)
        ax.set_title(f'Distribusi Review Score  ·  Rata-rata ★ {avg_review:.2f}',
                     fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, color=COLOR_PASTEL)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_facecolor('white')
        labels  = ['Tepat / Lebih Cepat', 'Terlambat']
        values  = [ontime_pct, late_pct]
        colors  = [COLOR_TEAL_DARK, COLOR_PRIMARY]
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.1f%%',
            startangle=90, colors=colors,
            wedgeprops={'edgecolor':'white', 'linewidth':2})
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
            autotext.set_color('white')
        ax.set_title('Status Pengiriman', fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.markdown(f"<p style='text-align:center; font-size:11px; color:#999; font-style:italic;'>Total: {total_del:,} | Tepat: {ontime_orders:,} | Terlambat: {late_orders:,}</p>",
                    unsafe_allow_html=True)

    st.info(f"💡 **Insight:** {ontime_pct:.1f}% order terkirim tepat waktu atau lebih cepat. Rata-rata waktu pengiriman **{avg_days:.1f} hari**.")

# ==================== TAB 5 ====================
with tab5:
    st.subheader("🗺️ Geospatial & Clustering Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='filter-inline-label'>Distribusi Pelanggan per Provinsi (Top 10)</p>",
                    unsafe_allow_html=True)
        state_counts = customers_geo.groupby('customer_state')['customer_id'].count().reset_index()
        state_counts.columns = ['state_code', 'count']
        state_counts['state'] = state_counts['state_code'].map(STATE_NAMES).fillna(state_counts['state_code'])
        state_counts = state_counts.sort_values('count', ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor('white')
        ax.set_facecolor(COLOR_CREAM)
        colors_geo = [COLOR_PRIMARY if i == 0 else COLOR_TEAL for i in range(len(state_counts))]
        bars = ax.barh(state_counts['state'], state_counts['count'],
                       color=colors_geo, edgecolor='white')
        for bar, val in zip(bars, state_counts['count']):
            ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=9,
                    color=COLOR_TEAL_DARK, fontweight='bold')
        ax.set_title('Top 10 Provinsi — Jumlah Pelanggan', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, color=COLOR_PASTEL)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("<p class='filter-inline-label'>Spending Cluster Pelanggan</p>",
                    unsafe_allow_html=True)
        bins   = [0, 100, 300, 600, float('inf')]
        labels = ['Low Spender', 'Medium Spender', 'High Spender', 'Premium Spender']
        rfm_data['Spending_Cluster'] = pd.cut(rfm_data['Monetary'], bins=bins, labels=labels)
        cluster_counts = rfm_data['Spending_Cluster'].value_counts().reset_index()
        cluster_counts.columns = ['Cluster', 'Count']
        cluster_counts['Cluster'] = pd.Categorical(cluster_counts['Cluster'],
                                                    categories=labels, ordered=True)
        cluster_counts = cluster_counts.sort_values('Cluster')
        cluster_colors = [COLOR_PASTEL, COLOR_SECONDARY, COLOR_PRIMARY, COLOR_TEAL_DARK]

        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor('white')
        ax.set_facecolor(COLOR_CREAM)
        bars = ax.barh(cluster_counts['Cluster'].astype(str), cluster_counts['Count'],
                       color=cluster_colors, edgecolor='white')
        for bar, val in zip(bars, cluster_counts['Count']):
            ax.text(bar.get_width() + cluster_counts['Count'].max()*0.01,
                    bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=9,
                    color=COLOR_TEAL_DARK, fontweight='bold')
        ax.set_title('Distribusi Spending Cluster', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, color=COLOR_PASTEL)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # ── Choropleth Map ──
    st.markdown("<p class='filter-inline-label' style='margin-top:1rem;'>Peta Distribusi Pelanggan per Provinsi Brazil</p>",
                unsafe_allow_html=True)

    with open('dashboard/brazil_states.geojson', 'r') as f:
        brazil_geo = json.load(f)

    state_map = customers_geo.groupby('customer_state')['customer_id'].count().reset_index()
    state_map.columns = ['sigla', 'customer_count']

    m = folium.Map(
        location=[-15.77972, -47.92972],
        zoom_start=4,
        tiles='CartoDB positron'
    )

    choropleth = folium.Choropleth(
        geo_data=brazil_geo,
        name='Distribusi Pelanggan',
        data=state_map,
        columns=['sigla', 'customer_count'],
        key_on='feature.properties.sigla',
        fill_color='YlOrRd',
        fill_opacity=0.8,
        line_opacity=0.6,
        line_color='white',
        legend_name='Jumlah Pelanggan',
        highlight=True
    ).add_to(m)

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['name', 'sigla'],
            aliases=['Provinsi:', 'Kode:'],
            style="font-family: Arial; font-size: 12px;"
        )
    )

    for feature in brazil_geo['features']:
        sigla = feature['properties']['sigla']
        name  = feature['properties']['name']
        count = state_map[state_map['sigla'] == sigla]['customer_count'].values
        count = int(count[0]) if len(count) > 0 else 0

        try:
            if feature['geometry']['type'] == 'Polygon':
                pts = feature['geometry']['coordinates'][0]
            else:
                pts = max(feature['geometry']['coordinates'],
                          key=lambda x: len(x[0]))[0]
            lng = sum(p[0] for p in pts) / len(pts)
            lat = sum(p[1] for p in pts) / len(pts)

            folium.Marker(
                location=[lat, lng],
                icon=folium.DivIcon(
                    html=f"""<div style="
                        font-family: Arial;
                        font-size: 9px;
                        font-weight: bold;
                        color: #2C687B;
                        text-align: center;
                        white-space: nowrap;">
                        {sigla}<br>{count:,}
                    </div>""",
                    icon_size=(50, 30),
                    icon_anchor=(25, 15)
                )
            ).add_to(m)
        except Exception:
            pass

    folium.LayerControl().add_to(m)
    folium_static(m, width=1200, height=500)

    st.info("💡 **Insight:** São Paulo mendominasi dengan pelanggan terbanyak. Mayoritas pelanggan masuk kategori **Low Spender** (belanja < R$100).")

# ===== FOOTER =====
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#aaa; font-size:12px;
            font-style:italic; padding:1rem;'>
    Proyek Analisis Data — Brazilian E-Commerce (Olist) &nbsp;|&nbsp; 2016–2018
</div>
""", unsafe_allow_html=True)