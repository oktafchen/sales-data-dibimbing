import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Bootcamp Enrollment Dashboard",
    layout="wide"
)

# =========================
# 1. LOAD & PREPROCESS DATA
# =========================

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)

    # --- Date handling ---
    df['Tanggal Gabungan_fix'] = pd.to_datetime(
        df['Tanggal Gabungan_fix'],
        errors='coerce'
    )

    df['Month_Only'] = df['Tanggal Gabungan_fix'].dt.to_period('M').astype(str)

    # --- Simplify Channel ---
    top_channels = df['Channel'].value_counts().head(5).index
    df['Channel_Simple'] = df['Channel'].apply(
        lambda x: x if x in top_channels else 'Others'
    )

    return df


# =========================
# 2. SIDEBAR — DATA INPUT
# =========================

st.sidebar.title("📂 Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info("⬅️ Upload dataset CSV untuk mulai dashboard.")
    st.stop()

df = load_data(uploaded_file)


# =========================
# 3. SIDEBAR — GLOBAL FILTER
# =========================

st.sidebar.title("🎛️ Filter")

# Date filter
min_date = df['Tanggal Gabungan_fix'].min()
max_date = df['Tanggal Gabungan_fix'].max()

date_range = st.sidebar.date_input(
    "Tanggal",
    [min_date, max_date]
)

# Product filter
product_options = sorted(df['Product'].dropna().unique())
selected_products = st.sidebar.multiselect(
    "Product",
    product_options,
    default=product_options
)

# Channel filter
channel_options = sorted(df['Channel_Simple'].dropna().unique())
selected_channels = st.sidebar.multiselect(
    "Channel",
    channel_options,
    default=channel_options
)

# Job category filter
job_options = sorted(df['Kategori_Pekerjaan_Simple'].dropna().unique())
selected_jobs = st.sidebar.multiselect(
    "Status Pekerjaan",
    job_options,
    default=job_options
)


# =========================
# 4. APPLY FILTER
# =========================

df_filtered = df[
    (df['Tanggal Gabungan_fix'] >= pd.to_datetime(date_range[0])) &
    (df['Tanggal Gabungan_fix'] <= pd.to_datetime(date_range[1])) &
    (df['Product'].isin(selected_products)) &
    (df['Channel_Simple'].isin(selected_channels)) &
    (df['Kategori_Pekerjaan_Simple'].isin(selected_jobs))
]


# =========================
# 5. SECTION 1 — OVERVIEW KPI
# =========================

st.title("🎓 Bootcamp Enrollment Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Peserta", len(df_filtered))

with col2:
    top_product = df_filtered['Product'].value_counts().idxmax()
    st.metric("Top Product", top_product)

with col3:
    top_channel = df_filtered['Channel_Simple'].value_counts().idxmax()
    st.metric("Top Channel", top_channel)

with col4:
    job_pct = (df_filtered['Kategori_Pekerjaan_Simple'] == 'Job Seeker').mean() * 100
    st.metric("% Job Seeker", f"{job_pct:.1f}%")

with col5:
    period = f"{df_filtered['Tanggal Gabungan_fix'].min().date()} – {df_filtered['Tanggal Gabungan_fix'].max().date()}"
    st.metric("Periode Data", period)


st.divider()

# =========================
# 6. SECTION 2 — PRODUCT & CHANNEL PERFORMANCE
# =========================

st.subheader("📊 Product & Channel Performance")

# Placeholder chart (nanti kita isi)
st.info("➡️ Grafik Product & Channel akan ditambahkan di sini.")

st.divider()

# =========================
# 7. SECTION 3 — PARTICIPANT PROFILE
# =========================

st.subheader("👥 Participant Profile")

st.info("➡️ Visual profil peserta akan ditambahkan di sini.")

st.divider()

# =========================
# 8. SECTION 4 — DEEP DIVE (META ADS → DATA SCIENCE)
# =========================

st.subheader("🔍 Deep Dive: Meta Ads → Data Science")

if (
    selected_channels == ['Meta Ads'] and
    selected_products == ['Data Science']
):
    st.success("Menampilkan deep dive untuk Meta Ads → Data Science")
else:
    st.warning("Pilih Channel = Meta Ads dan Product = Data Science untuk melihat deep dive.")

st.divider()

# =========================
# 9. SECTION 5 — STRATEGIC RECOMMENDATION
# =========================

st.subheader("🎯 Strategic Recommendations")

st.markdown("""
**Rekomendasi Utama:**
- Fokuskan Meta Ads untuk Data Science.
- Gunakan channel berbeda untuk product non-Data Science.
- Sesuaikan messaging dengan motivasi peserta (career switch, job outcome).
""")
# =========================
# 6. SECTION 2 — PRODUCT & CHANNEL PERFORMANCE
# =========================

st.subheader("📊 Product & Channel Performance")

# --- Bar: Participants per Product ---
prod_counts = (
    df_filtered['Product']
    .value_counts()
    .sort_values(ascending=False)
)

fig1, ax1 = plt.subplots(figsize=(6,4))
sns.barplot(
    x=prod_counts.values,
    y=prod_counts.index,
    ax=ax1
)
ax1.set_title("Jumlah Peserta per Product")
ax1.set_xlabel("Jumlah Peserta")
ax1.set_ylabel("Product")
st.pyplot(fig1)

# --- Stacked Bar (COUNT): Channel per Product ---
pivot_count = pd.crosstab(
    df_filtered['Product'],
    df_filtered['Channel_Simple']
)

fig2, ax2 = plt.subplots(figsize=(8,4))
pivot_count.plot(
    kind='bar',
    stacked=True,
    ax=ax2
)
ax2.set_title("Distribusi Channel per Product (Count)")
ax2.set_xlabel("Product")
ax2.set_ylabel("Jumlah Peserta")
ax2.legend(title="Channel", bbox_to_anchor=(1,1))
plt.xticks(rotation=45)
st.pyplot(fig2)


# --- Stacked Bar (%): Channel per Product ---
pivot_pct = pd.crosstab(
    df_filtered['Product'],
    df_filtered['Channel_Simple'],
    normalize='index'
) * 100

fig3, ax3 = plt.subplots(figsize=(8,4))
pivot_pct.plot(
    kind='bar',
    stacked=True,
    ax=ax3
)
ax3.set_title("Proporsi Channel per Product (%)")
ax3.set_xlabel("Product")
ax3.set_ylabel("Persentase (%)")
ax3.legend(title="Channel", bbox_to_anchor=(1,1))
plt.xticks(rotation=45)
st.pyplot(fig3)



# =========================
# 7. SECTION 3 — PARTICIPANT PROFILE
# =========================
st.subheader("👥 Participant Profile")

# --- Stacked Bar (%): Job Category per Product ---
job_pct = pd.crosstab(
    df_filtered['Product'],
    df_filtered['Kategori_Pekerjaan_Simple'],
    normalize='index'
) * 100

fig4, ax4 = plt.subplots(figsize=(8,4))
job_pct.plot(
    kind='bar',
    stacked=True,
    ax=ax4
)
ax4.set_title("Proporsi Status Pekerjaan per Product (%)")
ax4.set_xlabel("Product")
ax4.set_ylabel("Persentase (%)")
ax4.legend(title="Status Pekerjaan", bbox_to_anchor=(1,1))
plt.xticks(rotation=45)
st.pyplot(fig4)

if 'Umur' in df_filtered.columns and df_filtered['Umur'].notna().sum() > 0:
    fig5, ax5 = plt.subplots(figsize=(6,4))
    sns.boxplot(
        data=df_filtered,
        x='Product',
        y='Umur',
        ax=ax5
    )
    ax5.set_title("Distribusi Umur Peserta per Product")
    ax5.set_xlabel("Product")
    ax5.set_ylabel("Umur")
    plt.xticks(rotation=45)
    st.pyplot(fig5)
else:
    st.info("Data umur tidak tersedia untuk visualisasi.")

st.subheader("🎓 Latar Pendidikan (Top 10 Jurusan)")

top_jurusan = (
    df_filtered['Jurusan pendidikan']
    .value_counts()
    .head(10)
)

fig6, ax6 = plt.subplots(figsize=(6,4))
sns.barplot(
    x=top_jurusan.values,
    y=top_jurusan.index,
    ax=ax6
)
ax6.set_title("Top 10 Jurusan Pendidikan Peserta")
ax6.set_xlabel("Jumlah Peserta")
ax6.set_ylabel("Jurusan")
st.pyplot(fig6)


# =========================
# 8. SECTION 4 — DEEP DIVE (META ADS → DATA SCIENCE)
# =========================

st.subheader("🔍 Deep Dive: Meta Ads → Data Science")

# Kondisi aktivasi deep dive
is_meta_only = (set(selected_channels) == {'Meta Ads'})
is_ds_only = (set(selected_products) == {'Data Science'})

if not (is_meta_only and is_ds_only):
    st.info("Pilih **Channel = Meta Ads** dan **Product = Data Science** untuk melihat deep dive.")
    st.stop()

# =========================
# ISOLATE DATA
# =========================
meta_all = df_filtered[df_filtered['Channel_Simple'] == 'Meta Ads']
meta_ds = meta_all[meta_all['Product'] == 'Data Science']
meta_non_ds = meta_all[meta_all['Product'] != 'Data Science']

# =========================
# 4.1 KPI KECIL (PEMBUKTIAN CEPAT)
# =========================
colA, colB, colC = st.columns(3)

with colA:
    ds_share_meta = (meta_all['Product'] == 'Data Science').mean() * 100
    st.metric("% Data Science di Meta Ads", f"{ds_share_meta:.1f}%")

with colB:
    job_seeker_ds = (meta_ds['Kategori_Pekerjaan_Simple'] == 'Job Seeker').mean() * 100
    st.metric("% Job Seeker (DS)", f"{job_seeker_ds:.1f}%")

with colC:
    avg_age_ds = meta_ds['Umur_num'].mean() if 'Umur_num' in meta_ds.columns else np.nan
    st.metric("Rata-rata Umur (DS)", "-" if np.isnan(avg_age_ds) else f"{avg_age_ds:.1f}")

st.divider()

# =========================
# 4.2 STATUS PEKERJAAN: DS vs NON-DS
# =========================
st.markdown("### Status Pekerjaan (DS vs Non-DS)")

job_compare = pd.crosstab(
    meta_all['Kategori_Pekerjaan_Simple'],
    meta_all['Product'] == 'Data Science',
    normalize='columns'
) * 100

fig7, ax7 = plt.subplots(figsize=(6,4))
job_compare.plot(kind='bar', ax=ax7)
ax7.set_title("Proporsi Status Pekerjaan di Meta Ads")
ax7.set_xlabel("Status Pekerjaan")
ax7.set_ylabel("Persentase (%)")
ax7.legend(["Non Data Science", "Data Science"])
plt.xticks(rotation=45)
st.pyplot(fig7)

st.divider()

# =========================
# 4.3 DISTRIBUSI UMUR: DS vs NON-DS
# =========================
st.markdown("### Distribusi Umur")

if 'Umur_num' in meta_all.columns and meta_all['Umur_num'].notna().sum() > 0:
    fig8, ax8 = plt.subplots(figsize=(6,4))
    sns.boxplot(
        data=meta_all,
        x=meta_all['Product'] == 'Data Science',
        y='Umur_num',
        ax=ax8
    )
    ax8.set_xticklabels(['Non Data Science', 'Data Science'])
    ax8.set_title("Distribusi Umur Peserta Meta Ads")
    ax8.set_xlabel("")
    ax8.set_ylabel("Umur")
    st.pyplot(fig8)
else:
    st.info("Data umur tidak tersedia untuk analisis.")

st.divider()

# =========================
# 4.4 INSIGHT OTOMATIS (TEXT, BUKAN CHART)
# =========================
st.markdown("### Insight Utama")

insights = []

if ds_share_meta > 35:
    insights.append("Meta Ads menunjukkan **product–market fit yang kuat** untuk Data Science.")

if job_seeker_ds > 50:
    insights.append("Peserta Data Science dari Meta Ads **didominasi Job Seeker**, menunjukkan orientasi career switch.")

if not np.isnan(avg_age_ds) and avg_age_ds <= 27:
    insights.append("Rata-rata umur peserta berada pada **early career stage**, cocok untuk upskilling intensif.")

if len(insights) == 0:
    insights.append("Tidak ditemukan perbedaan signifikan pada filter saat ini.")

for i in insights:
    st.success(i)
st.subheader("🔍 Deep Dive: Meta Ads → Data Science")

# Kondisi aktivasi deep dive
is_meta_only = (set(selected_channels) == {'Meta Ads'})
is_ds_only = (set(selected_products) == {'Data Science'})

if not (is_meta_only and is_ds_only):
    st.info("Pilih **Channel = Meta Ads** dan **Product = Data Science** untuk melihat deep dive.")
    st.stop()

# =========================
# ISOLATE DATA
# =========================
meta_all = df_filtered[df_filtered['Channel_Simple'] == 'Meta Ads']
meta_ds = meta_all[meta_all['Product'] == 'Data Science']
meta_non_ds = meta_all[meta_all['Product'] != 'Data Science']

# =========================
# 4.1 KPI KECIL (PEMBUKTIAN CEPAT)
# =========================
colA, colB, colC = st.columns(3)

with colA:
    ds_share_meta = (meta_all['Product'] == 'Data Science').mean() * 100
    st.metric("% Data Science di Meta Ads", f"{ds_share_meta:.1f}%")

with colB:
    job_seeker_ds = (meta_ds['Kategori_Pekerjaan_Simple'] == 'Job Seeker').mean() * 100
    st.metric("% Job Seeker (DS)", f"{job_seeker_ds:.1f}%")

with colC:
    avg_age_ds = meta_ds['Umur_num'].mean() if 'Umur_num' in meta_ds.columns else np.nan
    st.metric("Rata-rata Umur (DS)", "-" if np.isnan(avg_age_ds) else f"{avg_age_ds:.1f}")

st.divider()

# =========================
# 4.2 STATUS PEKERJAAN: DS vs NON-DS
# =========================
st.markdown("### Status Pekerjaan (DS vs Non-DS)")

job_compare = pd.crosstab(
    meta_all['Kategori_Pekerjaan_Simple'],
    meta_all['Product'] == 'Data Science',
    normalize='columns'
) * 100

fig7, ax7 = plt.subplots(figsize=(6,4))
job_compare.plot(kind='bar', ax=ax7)
ax7.set_title("Proporsi Status Pekerjaan di Meta Ads")
ax7.set_xlabel("Status Pekerjaan")
ax7.set_ylabel("Persentase (%)")
ax7.legend(["Non Data Science", "Data Science"])
plt.xticks(rotation=45)
st.pyplot(fig7)

st.divider()

# =========================
# 4.3 DISTRIBUSI UMUR: DS vs NON-DS
# =========================
st.markdown("### Distribusi Umur")

if 'Umur_num' in meta_all.columns and meta_all['Umur_num'].notna().sum() > 0:
    fig8, ax8 = plt.subplots(figsize=(6,4))
    sns.boxplot(
        data=meta_all,
        x=meta_all['Product'] == 'Data Science',
        y='Umur_num',
        ax=ax8
    )
    ax8.set_xticklabels(['Non Data Science', 'Data Science'])
    ax8.set_title("Distribusi Umur Peserta Meta Ads")
    ax8.set_xlabel("")
    ax8.set_ylabel("Umur")
    st.pyplot(fig8)
else:
    st.info("Data umur tidak tersedia untuk analisis.")

st.divider()

# =========================
# 4.4 INSIGHT OTOMATIS (TEXT, BUKAN CHART)
# =========================
st.markdown("### Insight Utama")

insights = []

if ds_share_meta > 35:
    insights.append("Meta Ads menunjukkan **product–market fit yang kuat** untuk Data Science.")

if job_seeker_ds > 50:
    insights.append("Peserta Data Science dari Meta Ads **didominasi Job Seeker**, menunjukkan orientasi career switch.")

if not np.isnan(avg_age_ds) and avg_age_ds <= 27:
    insights.append("Rata-rata umur peserta berada pada **early career stage**, cocok untuk upskilling intensif.")

if len(insights) == 0:
    insights.append("Tidak ditemukan perbedaan signifikan pada filter saat ini.")

for i in insights:
    st.success(i)


