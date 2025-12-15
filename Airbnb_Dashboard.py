import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import zipfile, os

# ============================================================
# GLOBAL THEME
# ============================================================
MAIN_COLOR = "#1f77b4"
plt.rcParams["axes.prop_cycle"] = plt.cycler(color=[MAIN_COLOR])
plt.style.use("ggplot")

def add_bar_labels(ax):
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f"{height:.0f}", (p.get_x() + p.get_width()/2, height),
                    ha="center", va="bottom", fontsize=8)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    if os.path.exists("Airbnb_Open_Data_Final_features.csv.zip"):
        with zipfile.ZipFile("Airbnb_Open_Data_Final_features.csv.zip", 'r') as zip_ref:
            zip_ref.extractall()
    df = pd.read_csv("Airbnb_Open_Data_Final_features.csv")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df

df = load_data()

# ============================================================
# SIDEBAR FILTERS (Option C)
# ============================================================
st.sidebar.title("🔎 Filters")

# Multiselect filters
ng = st.sidebar.multiselect(
    "Neighbourhood Group",
    df["neighbourhood group"].dropna().unique().tolist(),
    default=df["neighbourhood group"].dropna().unique().tolist()
)

rt = st.sidebar.multiselect(
    "Room Type",
    df["room type"].dropna().unique().tolist(),
    default=df["room type"].dropna().unique().tolist()
)

co = st.sidebar.multiselect(
    "Country",
    df["country"].dropna().unique().tolist(),
    default=df["country"].dropna().unique().tolist()
)

# Single dropdown filters
if "availability_group" in df.columns:
    ag = st.sidebar.selectbox(
        "Availability Group",
        ["All"] + df["availability_group"].dropna().unique().tolist()
    )
else:
    ag = "All"

if "host_is_big" in df.columns:
    host_type = st.sidebar.selectbox(
        "Host Type",
        ["All", "Small Hosts (≤3 listings)", "Big Hosts (>3 listings)"]
    )
else:
    host_type = "All"

# Sliders
min_price, max_price = int(df["price"].min()), int(df["price"].max())
price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))

year_min, year_max = int(df["Construction year"].min()), int(df["Construction year"].max())
year_range = st.sidebar.slider("Construction Year Range", year_min, year_max, (year_min, year_max))

mn_min, mn_max = int(df["minimum nights"].min()), int(df["minimum nights"].max())
min_nights = st.sidebar.slider("Minimum Nights", mn_min, mn_max, (mn_min, mn_max))

# ============================================================
# APPLY FILTERS
# ============================================================
filtered = df.copy()

filtered = filtered[
    (filtered["neighbourhood group"].isin(ng)) &
    (filtered["room type"].isin(rt)) &
    (filtered["country"].isin(co)) &
    (filtered["price"] >= price_range[0]) &
    (filtered["price"] <= price_range[1]) &
    (filtered["Construction year"] >= year_range[0]) &
    (filtered["Construction year"] <= year_range[1]) &
    (filtered["minimum nights"] >= min_nights[0]) &
    (filtered["minimum nights"] <= min_nights[1])
]

if ag != "All":
    filtered = filtered[filtered["availability_group"] == ag]

if host_type != "All":
    if "Small" in host_type:
        filtered = filtered[filtered["host_is_big"] == 0]
    else:
        filtered = filtered[filtered["host_is_big"] == 1]

st.session_state["df"] = filtered

# ============================================================
# PAGE NAVIGATION (Option 3 names)
# ============================================================
page = st.sidebar.radio(
    "📄 Pages",
    [
        "Dashboard",
        "Market Supply",
        "Price Structure",
        "Demand & Occupancy",
        "Host Dynamics",
        "Feature Insights",
        "Statistical Correlation",
        "Geo Distribution",
        "Strategic Findings"
    ]
)

# ============================================================
# PAGE 1 — Dashboard
# ============================================================
if page == "Dashboard":
    st.title("📊 Airbnb Analytics — Executive Dashboard")

    df2 = st.session_state["df"]

    st.markdown("### Key Performance Indicators (Filtered Dataset)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Listings", f"{len(df2):,}")
    col2.metric("Unique Hosts", df2["NAME"].nunique())
    col3.metric("Average Price", f"${df2['price'].mean():.1f}")
    col4.metric("Average Rating", f"{df2['review rate number'].mean():.2f}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Avg Min Nights", f"{df2['minimum nights'].mean():.1f}")
    col6.metric("Avg Occupancy", f"{df2['occupancy_rate'].mean():.1f}")
    col7.metric("Avg Popularity", f"{df2['popularity_score'].mean():.1f}")
    col8.metric("Countries", df2["country"].nunique())

    st.markdown("---")
    st.write("Use the left sidebar to explore the full analytical pages.")
# ============================================================
# PAGE 2 — MARKET SUPPLY
# ============================================================
if page == "Market Supply":
    st.title("🏙 Market Supply Analysis")

    df2 = st.session_state["df"]

    st.header("1. Distribution of Listings")

    col1, col2 = st.columns(2)

    # --------------------------- #
    # Listings per Neighborhood Group
    # --------------------------- #
    with col1:
        st.subheader("Listings per Neighbourhood Group")
        counts = df2["neighbourhood group"].value_counts()
        if not counts.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(counts.index, counts.values)
            plt.xticks(rotation=45)
            add_bar_labels(ax)
            st.pyplot(fig)
            st.caption("Shows which major areas have the highest supply of listings.")

    # --------------------------- #
    # Listings per Room Type
    # --------------------------- #
    with col2:
        st.subheader("Listings per Room Type")
        rc = df2["room type"].value_counts()
        if not rc.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(rc.index, rc.values)
            add_bar_labels(ax)
            st.pyplot(fig)
            st.caption("Illustrates the distribution of listings across room categories.")

    col3, col4 = st.columns(2)

    # --------------------------- #
    # Listings per Country
    # --------------------------- #
    with col3:
        st.subheader("Listings per Country")
        cc = df2["country"].value_counts()
        if not cc.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(cc.index, cc.values)
            plt.xticks(rotation=45)
            add_bar_labels(ax)
            st.pyplot(fig)
            st.caption("Shows countries represented in the filtered dataset.")

    # --------------------------- #
    # Top 10 Neighbourhoods
    # --------------------------- #
    with col4:
        st.subheader("Top 10 Neighbourhoods")
        tn = df2["neighbourhood"].value_counts().head(10)
        if not tn.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(tn.index, tn.values)
            plt.xticks(rotation=45)
            add_bar_labels(ax)
            st.pyplot(fig)
            st.caption("Top neighbourhoods by listing count.")

# ============================================================
# PAGE 3 — PRICE STRUCTURE
# ============================================================
if page == "Price Structure":
    st.title("💰 Price Structure Analysis")

    df2 = st.session_state["df"]

    st.header("2. Pricing Insights")

    col1, col2 = st.columns(2)

    # --------------------------- #
    # Price Distribution
    # --------------------------- #
    with col1:
        st.subheader("Price Distribution")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df2["price"], bins=50)
        ax.set_xlabel("Price")
        st.pyplot(fig)
        st.caption("Histogram showing the spread of prices across listings.")

    # --------------------------- #
    # Price by Room Type
    # --------------------------- #
    with col2:
        st.subheader("Price by Room Type")
        grouped = [df2[df2["room type"] == x]["price"] for x in df2["room type"].unique()]
        labels = df2["room type"].unique()

        fig, ax = plt.subplots(figsize=(8, 6))
        bp = ax.boxplot(grouped, labels=labels, patch_artist=True)
        for patch in bp["boxes"]:
            patch.set_facecolor(MAIN_COLOR)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        st.caption("Compares price differences between room types.")

    # --------------------------- #
    # Average Price by Neighbourhood Group
    # --------------------------- #
    st.subheader("Average Price by Neighbourhood Group")
    avg = df2.groupby("neighbourhood group")["price"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(avg.index, avg.values)
    plt.xticks(rotation=45)
    add_bar_labels(ax)
    st.pyplot(fig)
    st.caption("Shows price variations at the neighbourhood-group level.")

# ============================================================
# PAGE 4 — DEMAND & OCCUPANCY
# ============================================================
if page == "Demand & Occupancy":
    st.title("📆 Demand & Occupancy Analysis")

    df2 = st.session_state["df"]

    st.header("3. Demand Indicators")

    col1, col2 = st.columns(2)

    # --------------------------- #
    # Minimum Nights Distribution
    # --------------------------- #
    with col1:
        st.subheader("Minimum Nights Distribution")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df2["minimum nights"], bins=50)
        st.pyplot(fig)
        st.caption("Distribution of host-required minimum stays.")

    # --------------------------- #
    # Availability 365
    # --------------------------- #
    with col2:
        st.subheader("Availability (Days per Year)")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df2["availability 365"], bins=50)
        st.pyplot(fig)
        st.caption("How many days listings are open for booking.")

    col3, col4 = st.columns(2)

    # --------------------------- #
    # Price vs Availability
    # --------------------------- #
    with col3:
        st.subheader("Price vs Availability 365")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(df2["availability 365"], df2["price"], alpha=0.3)
        ax.set_xlabel("Available Days")
        ax.set_ylabel("Price")
        st.pyplot(fig)
        st.caption("Relationship between nightly price and yearly availability.")

    # --------------------------- #
    # Price vs Min Nights
    # --------------------------- #
    with col4:
        st.subheader("Price vs Minimum Nights")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(df2["minimum nights"], df2["price"], alpha=0.3)
        st.pyplot(fig)
        st.caption("Shows how minimum stay rules relate to pricing.")

    # --------------------------- #
    # Occupancy Rate
    # --------------------------- #
    st.subheader("Occupancy Rate Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df2["occupancy_rate"], bins=50)
    st.pyplot(fig)
    st.caption("Displays how often listings are booked throughout the year.")

    if "availability_group" in df2.columns:
        st.subheader("Average Price by Availability Group")
        avg = df2.groupby("availability_group")["price"].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(avg.index.astype(str), avg.values)
        add_bar_labels(ax)
        st.pyplot(fig)
        st.caption("Availability patterns linked with pricing.")

# ============================================================
# PAGE 5 — HOST DYNAMICS
# ============================================================
if page == "Host Dynamics":
    st.title("👨‍💼 Host Dynamics")

    df2 = st.session_state["df"]

    st.header("4. Host Behavior & Reviews")

    col1, col2 = st.columns(2)

    # --------------------------- #
    # Rating Distribution
    # --------------------------- #
    with col1:
        st.subheader("Rating Distribution")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df2["review rate number"], bins=20)
        st.pyplot(fig)
        st.caption("Distribution of listing ratings across hosts.")

    # --------------------------- #
    # Average Rating by Room Type
    # --------------------------- #
    with col2:
        st.subheader("Average Rating by Room Type")
        avg = df2.groupby("room type")["review rate number"].mean()
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(avg.index, avg.values)
        plt.xticks(rotation=45)
        add_bar_labels(ax)
        st.pyplot(fig)
        st.caption("Shows which room types have higher guest satisfaction.")

    col3, col4 = st.columns(2)

    # --------------------------- #
    # Number of Reviews Distribution
    # --------------------------- #
    with col3:
        st.subheader("Number of Reviews Distribution")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df2["number of reviews"], bins=50)
        st.pyplot(fig)
        st.caption("Shows how many reviews listings typically receive.")

    # --------------------------- #
    # Host Size — Small vs Big
    # --------------------------- #
    with col4:
        st.subheader("Host Type Distribution")
        counts = df2["host_is_big"].value_counts()
        labels = ["Small Hosts (≤3)", "Big Hosts (>3)"]
        values = [counts.get(0, 0), counts.get(1, 0)]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(labels, values)
        add_bar_labels(ax)
        st.pyplot(fig)
        st.caption("Comparison of small vs big host representation.")

    # --------------------------- #
    # Average Price by Host Type
    # --------------------------- #
    st.subheader("Average Price by Host Type")
    avg = df2.groupby("host_is_big")["price"].mean()
    labels = ["Small Hosts", "Big Hosts"]
    values = [avg.get(0, 0), avg.get(1, 0)]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, values)
    add_bar_labels(ax)
    st.pyplot(fig)
    st.caption("Shows whether large or small hosts price higher.")

# ============================================================
# PAGE 6 — FEATURE INSIGHTS
# ============================================================
if page == "Feature Insights":
    st.title("⚙ Feature Insights")

    df2 = st.session_state["df"]

    st.header("5. Engineered Feature Metrics")

    col1, col2 = st.columns(2)

    # Popularity Score
    with col1:
        st.subheader("Popularity Score Distribution")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df2["popularity_score"], bins=50)
        st.pyplot(fig)
        st.caption("Shows how popular listings are relative to demand.")

    # Price Per Minimum Night
    with col2:
        st.subheader("Price per Minimum Stay Night")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df2["price_per_minimum_night"], bins=50)
        st.pyplot(fig)
        st.caption("Represents the effective nightly cost for minimum stays.")

    st.subheader("Price Per Room")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df2["price_per_room"], bins=50)
    st.pyplot(fig)
    st.caption("Shows the engineered per-room pricing distribution.")

# ============================================================
# PAGE 7 — STATISTICAL CORRELATION
# ============================================================
if page == "Statistical Correlation":
    st.title("📊 Statistical Correlation")

    df2 = st.session_state["df"]

    st.header("6. Correlation Matrix")

    numeric = [
        "price", "minimum nights", "availability 365",
        "number of reviews", "reviews per month",
        "review rate number", "price_per_room",
        "price_per_minimum_night", "popularity_score",
        "occupancy_rate"
    ]

    df_corr = df2[numeric].corr()

    fig = px.imshow(df_corr, text_auto=True, color_continuous_scale="Blues")
    st.plotly_chart(fig)
    st.caption("Heatmap of feature relationships.")

# ============================================================
# PAGE 8 — GEO DISTRIBUTION (Your original map)
# ============================================================
if page == "Geo Distribution":
    st.title("🗺 Geographic Distribution")

    df2 = st.session_state["df"]

    st.header("7. World Map — Listings by Location")

    if {"lat", "long"}.issubset(df2.columns):
        fig = px.scatter_geo(
            df2.dropna(subset=["lat", "long"]),
            lat="lat",
            lon="long",
            color="price",
            hover_name="NAME",
            color_continuous_scale="Blues",
            title="Global Distribution of Listings (Colored by Price)"
        )
        st.plotly_chart(fig)
        st.caption("Interactive global map of Airbnb listings.")
    else:
        st.info("Location data not available for mapping.")
# ============================================================
# PAGE 9 — STRATEGIC FINDINGS (Fixed Professional Insights)
# ============================================================
if page == "Strategic Findings":
    st.title("⭐ Strategic Findings")

    df2 = st.session_state["df"]

    st.markdown("""
    ## Executive Summary  
    This section presents high-level, **fixed strategic insights** derived from the Airbnb dataset.  
    These insights reflect **common patterns**, **market signals**, and **business interpretations**  
    that apply regardless of filters.
    """)

    st.markdown("---")

    # -------------------------------------------------------
    # 1. Pricing Strategy
    # -------------------------------------------------------
    st.subheader("💰 1. Pricing Strategy Insights")

    st.write("""
    - Prices show **strong variance** across neighbourhood groups and room types,  
      indicating the need for **localized pricing models**.  
    - Entire homes consistently command the **highest prices**, while private/shared rooms  
      remain budget-friendly segments.  
    - Areas with higher availability tend to offer **slightly lower prices**, suggesting  
      competitive pressure in high-supply zones.
    """)

    st.markdown("---")

    # -------------------------------------------------------
    # 2. Host Behavior
    # -------------------------------------------------------
    st.subheader("👨‍💼 2. Host Behavior & Market Structure")

    st.write("""
    - The market shows a mix of **small hosts** (≤3 listings) and **professional hosts** (>3 listings).  
    - Professional hosts tend to manage multiple units, indicating growing **commercialization**  
      of the platform.  
    - Small hosts contribute significantly to market diversity and maintain competitive pricing.  
    """)

    st.markdown("---")

    # -------------------------------------------------------
    # 3. Demand & Occupancy
    # -------------------------------------------------------
    st.subheader("📆 3. Demand & Occupancy Trends")

    st.write("""
    - Occupancy rates suggest a **healthy level of guest demand**, especially in central  
      neighbourhood groups.  
    - Listings with lower minimum-night requirements show **higher turnover and occupancy**,  
      appealing to short-stay guests.  
    - High availability is often linked to **lower guest engagement** or **oversupply** in the area.  
    """)

    st.markdown("---")

    # -------------------------------------------------------
    # 4. Guest Experience & Ratings
    # -------------------------------------------------------
    st.subheader("⭐ 4. Guest Experience Insights")

    st.write("""
    - Rating averages remain **consistently high**, reflecting strong service levels among hosts.  
    - Room type influences rating — entire homes often receive slightly higher scores due to  
      privacy, comfort, and amenities.  
    - Listings with more reviews indicate **higher market visibility** and **trustworthiness**.  
    """)

    st.markdown("---")

    # -------------------------------------------------------
    # 5. Feature Engineering Insights
    # -------------------------------------------------------
    st.subheader("⚙ 5. Engineered Feature Perspective")

    st.write("""
    - Engineered metrics like **popularity score**, **price per minimum night**,  
      and **price per room** provide deeper analytical visibility.  
    - Popularity score highlights listings that outperform peers on engagement,  
      independent of price or availability.  
    - Price-per-room is a strong indicator of **host pricing strategy efficiency**.  
    """)

    st.markdown("---")

    # -------------------------------------------------------
    # 6. Neighbourhood Insights
    # -------------------------------------------------------
    st.subheader("🏙 6. Neighbourhood Performance Insights")

    st.write("""
    - Central neighbourhood groups dominate supply and demand, offering better  
      returns for hosts.  
    - Peripheral areas show competitive pricing but require **strong differentiators**  
      (reviews, amenities, or unique offerings) to increase visibility.  
    - High-density neighbourhoods show predictable pricing patterns and  
      **well-defined market segments**.  
    """)

    st.markdown("---")

    # -------------------------------------------------------
    # Final Conclusions
    # -------------------------------------------------------
    st.header("📌 Final Strategic Conclusions")

    st.success("""
    - The Airbnb market demonstrates strong diversity across pricing, host  
      behavior, and geographic distribution.  
    - Successful market strategy requires **targeted pricing**, strong **review  
      performance**, and optimized **availability management**.  
    - Hosts who align room type, competitive pricing, and service quality  
      outperform competitors consistently.
    """)

    st.caption("End of Strategic Report — Use filters to explore deeper insights.")

# END OF FILE


