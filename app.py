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
def simplify_job_category(x):
    x = str(x).lower()

    if 'job seeker' in x or 'jobseeker' in x or 'fresh graduate' in x:
        return 'Job Seeker'
    elif 'mahasiswa' in x or 'student' in x:
        return 'Mahasiswa'
    elif 'freelance' in x or 'wirausaha' in x or 'usaha' in x:
        return 'Freelance / Wirausaha'
    elif 'karyawan' in x or 'bekerja' in x or 'pegawai' in x:
        return 'Pekerja'
    else:
        return 'Others'
        
def simplify_motivation(x):
    x = str(x).lower()

    if any(k in x for k in ['cari kerja', 'job', 'kerja', 'career', 'fresh graduate']):
        return 'Job Seeking'
    elif any(k in x for k in ['switch', 'pindah', 'career change']):
        return 'Career Switching'
    elif any(k in x for k in ['upskill', 'belajar', 'skill', 'knowledge']):
        return 'Upskilling'
    else:
        return 'Others / Unclear'

   

def load_data(uploaded_file):
    df = pd.read_csv("df_sheet1 (1).csv")

    # Date handling
    if 'Tanggal Gabungan_fix' in df.columns:
        df['Tanggal Gabungan_fix'] = pd.to_datetime(df['Tanggal Gabungan_fix'], errors='coerce')
    else:
        df['Tanggal Gabungan_fix'] = pd.to_datetime(df['Tanggal Gabungan'], errors='coerce')

    df['Month_Only'] = df['Tanggal Gabungan_fix'].dt.to_period('M').astype(str)

    # Simplify Channel
    top_channels = df['Channel'].value_counts().head(5).index
    df['Channel_Simple'] = df['Channel'].apply(
        lambda x: x if x in top_channels else 'Others'
    )
    # 🔥 WAJIB ADA — INI KUNCI
    df['Kategori_Pekerjaan_Simple'] = df['Kategori Pekerjaan'].apply(
        simplify_job_category
    )
    if 'Motivasi mengikuti bootcamp' in df.columns:
        df['Motivation_Category'] = df['Motivasi mengikuti bootcamp'].apply(simplify_motivation)
    else:
        df['Motivation_Category'] = 'Unknown'

    
    return df
# =========================
# LOAD DATA
# =========================
df = load_data()

if df.empty:
    st.error("Dataset kosong atau gagal dibaca.")
    st.stop()
    
# =========================
# 2. BASIC STYLE (OPTIONAL)
# =========================
st.markdown("""
<style>
.kpi-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
.kpi-title {
    font-size: 14px;
    color: #9CA3AF;
}
.kpi-value {
    font-size: 26px;
    font-weight: bold;
    color: white;
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)


job_options = sorted(df['Kategori_Pekerjaan_Simple'].dropna().unique())




# 4. FEATURE PREP (RINGKAS)
# =========================
df_viz = df.copy()

df_viz['Month'] = df_viz['Tanggal Gabungan_fix'].dt.to_period('M').astype(str)




# =========================
# 5. SIDEBAR FILTER
# =========================
st.sidebar.header("🔎 Filter")

# Date filter
min_date = df_viz['Tanggal Gabungan_fix'].min()
max_date = df_viz['Tanggal Gabungan_fix'].max()

date_range = st.sidebar.date_input(
    "Periode Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
# =========================
# VALIDASI DATE RANGE
# =========================
if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
    st.warning("📅 Silakan pilih rentang tanggal (awal dan akhir).")
    st.stop()

start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

if start_date > end_date:
    st.warning("📅 Tanggal awal tidak boleh lebih besar dari tanggal akhir.")
    st.stop()
# Product filter
product_options = sorted(df_viz['Product'].dropna().unique())
selected_product = st.sidebar.multiselect(
    "Product",
    options=product_options,
    default=product_options
)

# Channel filter
channel_options = sorted(df_viz['Channel_Simple'].dropna().unique())
selected_channel = st.sidebar.multiselect(
    "Channel",
    options=channel_options,
    default=channel_options
)

# Job category filter
job_options = sorted(df_viz['Kategori_Pekerjaan_Simple'].dropna().unique())
selected_job = st.sidebar.multiselect(
    "Kategori Pekerjaan",
    options=job_options,
    default=job_options
)

# Apply filters
filtered_df = df_viz[
    (df_viz['Tanggal Gabungan_fix'] >= start_date) &
    (df_viz['Tanggal Gabungan_fix'] <= end_date) &
    (df_viz['Product'].isin(selected_product)) &
    (df_viz['Channel_Simple'].isin(selected_channel)) &
    (df_viz['Kategori_Pekerjaan_Simple'].isin(selected_job))
]

# =========================
# 6. KPI SECTION
# =========================
st.markdown("## 📊 Key Performance Indicators")

total_participants = len(filtered_df)

top_product = (
    filtered_df['Product']
    .value_counts()
    .idxmax()
    if not filtered_df.empty else "-"
)

top_channel = (
    filtered_df['Channel_Simple']
    .value_counts()
    .idxmax()
    if not filtered_df.empty else "-"
)

job_seeker_pct = (
    filtered_df['Kategori_Pekerjaan_Simple']
    .value_counts(normalize=True)
    .get('Job Seeker', 0) * 100
)

period_label = f"{date_range[0]} → {date_range[1]}"

col1, col2, col3, col4, col5 = st.columns(5)

def kpi_box(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

with col1:
    kpi_box("Total Peserta", f"{total_participants:,}")

with col2:
    kpi_box("Top Product", top_product)

with col3:
    kpi_box("Top Channel", top_channel)

with col4:
    kpi_box("% Job Seeker", f"{job_seeker_pct:.1f}%")

with col5:
    kpi_box("Periode Data", period_label)

# =========================
# 7. MAIN DASHBOARD CONTENT
# =========================
st.markdown("---")
st.markdown("## 📈 Overview")

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Trend Analysis",
    "Participant Profile",
    "Deep Dive"
])

with tab1:
    st.subheader("Distribusi Product (Top 10)")

    # =========================
    # PRODUCT CHART
    # =========================
    product_count = (
        filtered_df
        .groupby('Product')
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
        .head(10)
    )

    if product_count.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        top_value = product_count['count'].max()

        colors = [
            '#F97316' if v == top_value else '#3B82F6'
            for v in product_count['count']
        ]

        fig, ax = plt.subplots(figsize=(10, 5))

        bars = ax.bar(
            product_count['Product'],
            product_count['count'],
            color=colors
        )

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                int(height),
                ha='center',
                va='bottom',
                fontsize=9
            )

        ax.set_ylabel("Jumlah Peserta")
        ax.set_title("Product Terlaris")
        ax.set_xticklabels(
            product_count['Product'],
            rotation=45,
            ha='right'
        )
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        st.pyplot(fig)

    st.markdown("---")

    # =========================
    # CHANNEL CHART
    # =========================
    st.subheader("Distribusi Channel (Top 8)")

    channel_count = (
        filtered_df
        .groupby('Channel_Simple')
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
        .head(8)
    )

    if channel_count.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        top_value = channel_count['count'].max()

        colors = [
            '#F97316' if v == top_value else '#2563EB'
            for v in channel_count['count']
        ]

        fig, ax = plt.subplots(figsize=(10, 5))

        bars = ax.bar(
            channel_count['Channel_Simple'],
            channel_count['count'],
            color=colors
        )

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                int(height),
                ha='center',
                va='bottom',
                fontsize=9
            )

        ax.set_ylabel("Jumlah Peserta")
        ax.set_title("Kontribusi Channel")
        ax.set_xticklabels(
            channel_count['Channel_Simple'],
            rotation=30,
            ha='right'
        )
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        st.pyplot(fig)

        

with tab2:
    st.subheader("📉 Trend Analysis")

    # =========================
    # PREP DATA
    # =========================
    trend_df = (
        filtered_df
        .groupby('Month')
        .size()
        .reset_index(name='count')
        .sort_values('Month')
    )

    if trend_df.empty or len(trend_df) < 2:
        st.warning("Data tidak cukup untuk menampilkan trend.")
    else:
        max_row = trend_df.loc[trend_df['count'].idxmax()]
        min_row = trend_df.loc[trend_df['count'].idxmin()]

        fig, ax = plt.subplots(figsize=(11, 5))

        ax.plot(
            trend_df['Month'],
            trend_df['count'],
            marker='o',
            linewidth=2,
            color='#2563EB'
        )

        ax.scatter(max_row['Month'], max_row['count'], color='green', s=80)
        ax.scatter(min_row['Month'], min_row['count'], color='red', s=80)

        ax.text(
            max_row['Month'],
            max_row['count'] + (trend_df['count'].max() * 0.03),
            f"Max: {int(max_row['count'])}",
            ha='center',
            color='green',
            fontsize=9
        )

        ax.text(
            min_row['Month'],
            max(min_row['count'] - (trend_df['count'].max() * 0.05), 0),
            f"Min: {int(min_row['count'])}",
            ha='center',
            color='red',
            fontsize=9
        )

        ax.set_title("Trend Jumlah Peserta per Bulan")
        ax.set_xlabel("")
        ax.set_ylabel("Jumlah Peserta")
        ax.set_xticklabels(
            trend_df['Month'],
            rotation=45,
            ha='right'
        )

        ax.grid(axis='y', linestyle='--', alpha=0.4)

        st.pyplot(fig)


with tab3:
    st.subheader("Profil Peserta")

    col_a, col_b = st.columns(2)

    # ======================================================
    # A. JOB CATEGORY
    # ======================================================
    with col_a:
        st.markdown("### 👔 Kategori Pekerjaan (Top 7)")

        job_count = (
            filtered_df
            .groupby('Kategori_Pekerjaan_Simple')
            .size()
            .reset_index(name='count')
            .sort_values('count', ascending=False)
            .head(7)
        )

        if job_count.empty:
            st.warning("Tidak ada data.")
        else:
            top_value = job_count['count'].max()

            colors = [
                '#F97316' if v == top_value else '#3B82F6'
                for v in job_count['count']
            ]

            fig, ax = plt.subplots(figsize=(6,4))

            bars = ax.barh(
                job_count['Kategori_Pekerjaan_Simple'],
                job_count['count'],
                color=colors
            )

            for bar in bars:
                width = bar.get_width()
                ax.text(
                    width,
                    bar.get_y() + bar.get_height() / 2,
                    int(width),
                    va='center',
                    fontsize=9
                )

            ax.invert_yaxis()
            ax.set_xlabel("Jumlah Peserta")
            ax.set_ylabel("")
            ax.grid(axis='x', linestyle='--', alpha=0.4)

            st.pyplot(fig)

    # ======================================================
    # B. EDUCATION LEVEL
    # ======================================================
    with col_b:
        st.markdown("### 🎓 Level Pendidikan")

        edu_count = (
            filtered_df
            .groupby('Level pendidikan')
            .size()
            .reset_index(name='count')
            .sort_values('count', ascending=False)
        )

        if edu_count.empty:
            st.warning("Tidak ada data.")
        else:
            top_value = edu_count['count'].max()

            colors = [
                '#F97316' if v == top_value else '#2563EB'
                for v in edu_count['count']
            ]

            fig, ax = plt.subplots(figsize=(6,4))

            bars = ax.bar(
                edu_count['Level pendidikan'],
                edu_count['count'],
                color=colors
            )

            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    int(height),
                    ha='center',
                    va='bottom',
                    fontsize=9
                )

            ax.set_ylabel("Jumlah Peserta")
            ax.set_xlabel("")
            ax.set_xticklabels(
                edu_count['Level pendidikan'],
                rotation=30,
                ha='right'
            )
            ax.grid(axis='y', linestyle='--', alpha=0.4)

            st.pyplot(fig)

    st.markdown("---")

    # ======================================================
    # C. AGE DISTRIBUTION
    # ======================================================
    st.markdown("### 🎂 Distribusi Umur Peserta")

    age_df = filtered_df.copy()
    age_df['Umur'] = pd.to_numeric(age_df['Umur'], errors='coerce')

    age_df = age_df.dropna(subset=['Umur'])

    if age_df.empty:
        st.warning("Data umur tidak tersedia.")
    else:
        fig, ax = plt.subplots(figsize=(10,4))

        ax.hist(
            age_df['Umur'],
            bins=15,
            color='#3B82F6',
            edgecolor='white'
        )

        ax.set_xlabel("Umur")
        ax.set_ylabel("Jumlah Peserta")
        ax.set_title("Distribusi Umur Peserta")

        ax.grid(axis='y', linestyle='--', alpha=0.4)

        st.pyplot(fig)

with tab4:
    st.subheader("🔎 Deep Dive Analysis")

    st.markdown("### 📉 Enrollment Drop – April 2025")

    months_focus = ['2025-03', '2025-04', '2025-05']
    df_april = filtered_df[filtered_df['Month'].isin(months_focus)]

    if df_april.empty:
        st.warning("Data tidak cukup untuk analisis April 2025.")
    else:
        fig, ax = plt.subplots(figsize=(8,5))

        sns.countplot(
            data=df_april,
            x='Month',
            hue='Channel_Simple',
            ax=ax
        )

        ax.set_title("Channel Contribution Around April 2025")
        ax.set_xlabel("Month")
        ax.set_ylabel("Participants")
        ax.legend(title="Channel")

        st.pyplot(fig)
        st.markdown("---")
        st.markdown("### 🎯 Meta Ads Contribution to Data Science")
    
        df_ds = filtered_df[filtered_df['Product'] == 'Data Science']
    
        if df_ds.empty:
            st.warning("Tidak ada data Data Science.")
        else:
            channel_ds = (
                df_ds
                .groupby('Channel_Simple')
                .size()
                .reset_index(name='count')
                .sort_values('count', ascending=False)
                .head(6)
            )
    
            fig, ax = plt.subplots(figsize=(8,4))
    
            bars = ax.bar(
                channel_ds['Channel_Simple'],
                channel_ds['count'],
                color=['#F97316' if i == 0 else '#3B82F6' for i in range(len(channel_ds))]
            )
    
            for bar in bars:
                ax.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_height(),
                    int(bar.get_height()),
                    ha='center',
                    va='bottom'
                )
    
            ax.set_title("Top Channels for Data Science Enrollment")
            ax.set_ylabel("Participants")
            ax.set_xlabel("")
            ax.set_xticklabels(channel_ds['Channel_Simple'], rotation=30, ha='right')
    
            st.pyplot(fig)
            st.markdown("---")
            st.markdown("### 👤 Motivation vs Job Category")
        
            fig, ax = plt.subplots(figsize=(8,5))
        
            sns.countplot(
                data=filtered_df,
                x='Motivation_Category',
                hue='Kategori_Pekerjaan_Simple',
                ax=ax
            )
        
            ax.set_title("Motivation vs Job Category")
            ax.set_xlabel("Motivation")
            ax.set_ylabel("Participants")
            ax.legend(title="Job Category")
        
            st.pyplot(fig)



# =========================
# 9. FOOTER
# =========================
st.markdown("---")
st.caption("Dashboard dibuat untuk kebutuhan analisis sales & business insight.")





