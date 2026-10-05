import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# PAGE CONFIG
st.set_page_config(
    page_title="Food Delivery Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# COLOURS + CSS  (simple, normal colours)

COLORS = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", "#8C564B", "#17BECF"]
BLUE = "#1F77B4"

st.markdown(
    """
<style>
/* KPI cards */
.kpi {
    background: white; border: 1px solid #dfe3e8; border-top: 6px solid #1F77B4;
    border-radius: 12px; padding: 20px 14px; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 14px;
}
.kpi .label { font-size: 1.05rem; font-weight: 600; color: #555; }
.kpi .value { font-size: 2.3rem; font-weight: 800; color: #1a1a1a; margin-top: 6px; }

/* big summary paragraph at the bottom of each tab */
.summary {
    background: #f6f8fb; border: 1px solid #dfe3e8; border-left: 8px solid #1F77B4;
    border-radius: 12px; padding: 22px 28px; margin-top: 10px;
    font-size: 1.2rem; line-height: 1.8; color: #222;
}
.summary p { margin: 0 0 14px 0; }

/* tabs */
.stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; padding: 10px 20px; }
</style>
""",
    unsafe_allow_html=True,
)

# HELPER FUNCTIONS

def kpi_card(label, value):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def summary_box(*paragraphs):
    """Large summary paragraph(s) shown at the bottom of a tab."""
    st.subheader("📝 Summary & Insights")
    body = "".join(f"<p>{p}</p>" for p in paragraphs)
    st.markdown(f'<div class="summary">{body}</div>', unsafe_allow_html=True)


def show(fig, height=420):
    fig.update_layout(
        height=height,
        template="plotly_white",
        font=dict(size=14),
        title_font=dict(size=20),
        margin=dict(t=60, b=30, l=20, r=20),
        legend_title_text="",
    )
    st.plotly_chart(fig, use_container_width=True)

# LOAD DATA

@st.cache_data
def load_data():
    return pd.read_csv("data/food_delivery_cleaned.csv", parse_dates=["Order_Date"])


df = load_data()

# TITLE

st.title("🍔 Online Food Delivery Analysis Dashboard")
st.caption(
    "Interactive analysis of customer behaviour, revenue, delivery "
    "performance and restaurant operations."
)

# SIDEBAR FILTERS

st.sidebar.header("🔎 Dashboard Filters")

city_options = sorted(df["City"].dropna().unique())
cuisine_options = sorted(df["Cuisine_Type"].dropna().unique())
status_options = sorted(df["Order_Status"].dropna().unique())

selected_cities = st.sidebar.multiselect("🏙️ City", city_options, default=city_options)
selected_cuisines = st.sidebar.multiselect("🍛 Cuisine Type", cuisine_options, default=cuisine_options)
selected_status = st.sidebar.multiselect("📦 Order Status", status_options, default=status_options)

min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

filtered_df = df[
    df["City"].isin(selected_cities)
    & df["Cuisine_Type"].isin(selected_cuisines)
    & df["Order_Status"].isin(selected_status)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
    filtered_df = filtered_df[
        (filtered_df["Order_Date"] >= start_date) & (filtered_df["Order_Date"] < end_date)
    ]

if filtered_df.empty:
    st.warning("⚠️ No data matches the selected filters. Please widen your selection.")
    st.stop()

st.sidebar.divider()
st.sidebar.metric("Filtered Orders", f"{len(filtered_df):,}")
st.sidebar.metric("Filtered Revenue", f"₹{filtered_df['Final_Amount'].sum():,.0f}")

# KPI CALCULATIONS

total_orders = len(filtered_df)
total_revenue = filtered_df["Final_Amount"].sum()
avg_order_value = filtered_df["Final_Amount"].mean()
avg_delivery_time = filtered_df["Delivery_Time_Min"].mean()
cancellation_rate = filtered_df["Order_Status"].eq("Cancelled").mean() * 100
delivered_pct = filtered_df["Order_Status"].eq("Delivered").mean() * 100
avg_profit_margin = filtered_df["Profit_Margin_Pct"].mean()

delivered_only = filtered_df[filtered_df["Order_Status"] == "Delivered"]
avg_rating = delivered_only["Delivery_Rating"].mean() if not delivered_only.empty else 0.0
if pd.isna(avg_rating):
    avg_rating = 0.0

# KPI SECTION

st.subheader("📊 Key Performance Indicators")

row1 = st.columns(4)
with row1[0]:
    kpi_card("🛒 Total Orders", f"{total_orders:,}")
with row1[1]:
    kpi_card("💰 Total Revenue", f"₹{total_revenue:,.0f}")
with row1[2]:
    kpi_card("💵 Avg Order Value", f"₹{avg_order_value:,.0f}")
with row1[3]:
    kpi_card("🚚 Avg Delivery Time", f"{avg_delivery_time:.1f} min")

row2 = st.columns(4)
with row2[0]:
    kpi_card("❌ Cancellation Rate", f"{cancellation_rate:.1f}%")
with row2[1]:
    kpi_card("⭐ Avg Delivery Rating", f"{avg_rating:.2f} / 5")
with row2[2]:
    kpi_card("📈 Avg Profit Margin", f"{avg_profit_margin:.1f}%")
with row2[3]:
    kpi_card("✅ Delivery Success", f"{delivered_pct:.1f}%")

st.divider()

# TABS

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Revenue & Orders", "🚚 Delivery", "🍽️ Restaurants", "⚙️ Operations"]
)

# TAB 1 - REVENUE & ORDERS

with tab1:

    # ---- Chart 1: Monthly trend ----
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    metric_choice = st.radio(
        "Choose metric for the monthly trend:",
        ["Revenue", "Orders"],
        horizontal=True,
    )

    month_names = filtered_df["Order_Date"].dt.month_name()

    if metric_choice == "Revenue":
        monthly = filtered_df.groupby(month_names)["Final_Amount"].sum()
    else:
        monthly = filtered_df.groupby(month_names).size()

    monthly = monthly.reindex(month_order).dropna().reset_index()
    monthly.columns = ["Month", "Value"]

    fig = px.line(
        monthly, x="Month", y="Value", markers=True, text="Value",
        title=f"Monthly {metric_choice} Trend",
        labels={"Value": metric_choice},
        color_discrete_sequence=[BLUE],
    )
    fig.update_traces(
        texttemplate="₹%{text:,.0f}" if metric_choice == "Revenue" else "%{text:,.0f}",
        textposition="top center",
        hovertemplate="<b>%{x}</b><br>" + metric_choice + ": %{y:,.0f}<extra></extra>",
    )
    fig.update_yaxes(rangemode="tozero")
    show(fig)

    best_month = monthly.loc[monthly["Value"].idxmax()]
    worst_month = monthly.loc[monthly["Value"].idxmin()]

    # ---- Chart 2: Revenue breakdown ----
    group_choice = st.selectbox(
        "Break down revenue by:",
        ["City", "Cuisine_Type", "Customer_Age_Group"],
    )

    breakdown = (
        filtered_df.groupby(group_choice, observed=True)["Final_Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        breakdown, x=group_choice, y="Final_Amount", text="Final_Amount",
        color_discrete_sequence=[BLUE],
        title=f"Revenue by {group_choice.replace('_', ' ')}",
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis_title="Revenue (₹)")
    show(fig)

    top_group = breakdown.iloc[0][group_choice]
    top_group_share = breakdown.iloc[0]["Final_Amount"] / breakdown["Final_Amount"].sum() * 100

    # ---- Chart 3: Orders by day of week ----
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = (
        filtered_df["Order_Date"].dt.day_name()
        .value_counts()
        .reindex(day_order)
        .dropna()
        .reset_index()
    )
    day_counts.columns = ["Day", "Orders"]

    fig = px.bar(
        day_counts, x="Day", y="Orders", text="Orders",
        color_discrete_sequence=["#FF7F0E"],
        title="Orders by Day of the Week",
        labels={"Orders": "Number of Orders"},
    )
    fig.update_traces(textposition="outside")
    show(fig)

    busiest_day = day_counts.loc[day_counts["Orders"].idxmax()]
    weekend_share = (
        day_counts[day_counts["Day"].isin(["Saturday", "Sunday"])]["Orders"].sum()
        / day_counts["Orders"].sum() * 100
    )

    # ---- Summary paragraph ----
    summary_box(
        f"<b>KPI overview:</b> The selected data has <b>{total_orders:,}</b> orders that "
        f"generated a total revenue of <b>₹{total_revenue:,.0f}</b>. On average, each order is "
        f"worth <b>₹{avg_order_value:,.0f}</b> and the business earns an average profit margin "
        f"of <b>{avg_profit_margin:.1f}%</b>.",
        f"<b>Chart insights:</b> In the monthly {metric_choice.lower()} trend, "
        f"<b>{best_month['Month']}</b> is the best month (<b>{best_month['Value']:,.0f}</b>) "
        f"and <b>{worst_month['Month']}</b> is the weakest (<b>{worst_month['Value']:,.0f}</b>). "
        f"When revenue is split by {group_choice.replace('_', ' ').lower()}, "
        f"<b>{top_group}</b> is the top performer and contributes <b>{top_group_share:.1f}%</b> "
        f"of total revenue. The busiest day for orders is <b>{busiest_day['Day']}</b> with "
        f"<b>{busiest_day['Orders']:,}</b> orders, and weekends bring "
        f"<b>{weekend_share:.1f}%</b> of all orders.",
    )

# TAB 2 - DELIVERY

with tab2:

    # ---- Chart 1: Avg delivery time by city ----
    city_time = (
        filtered_df.groupby("City")["Delivery_Time_Min"]
        .mean().sort_values(ascending=False).reset_index()
    )

    fig = px.bar(
        city_time, x="City", y="Delivery_Time_Min", text="Delivery_Time_Min",
        color_discrete_sequence=[BLUE],
        title="Average Delivery Time by City (minutes)",
        labels={"Delivery_Time_Min": "Avg Delivery Time (min)"},
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    show(fig)

    slow_city = city_time.iloc[0]
    fast_city = city_time.iloc[-1]

    # ---- Chart 2: Distance vs delivery time ----
    sample_df = filtered_df.sample(min(3000, len(filtered_df)), random_state=42)

    fig = px.scatter(
        sample_df, x="Distance_km", y="Delivery_Time_Min",
        color="Delivery_Performance", opacity=0.6,
        color_discrete_sequence=COLORS,
        hover_data=["City"],
        title="Distance vs Delivery Time",
        labels={"Distance_km": "Distance (km)", "Delivery_Time_Min": "Delivery Time (min)"},
    )
    show(fig)

    avg_distance = filtered_df["Distance_km"].mean()
    corr = filtered_df["Distance_km"].corr(filtered_df["Delivery_Time_Min"])
    if pd.isna(corr):
        relation_text = "could not be measured with the current selection"
    else:
        strength = "strong" if abs(corr) > 0.6 else "moderate" if abs(corr) > 0.3 else "weak"
        relation_text = f"is {strength} (correlation {corr:.2f})"

    # ---- Chart 3: Delivery performance breakdown ----
    perf = filtered_df["Delivery_Performance"].value_counts().reset_index()
    perf.columns = ["Performance", "Orders"]

    fig = px.pie(
        perf, names="Performance", values="Orders", hole=0.45,
        color_discrete_sequence=COLORS,
        title="Delivery Performance Breakdown",
    )
    fig.update_traces(textinfo="label+percent+value", textfont_size=14)
    show(fig)

    top_perf = perf.iloc[0]
    top_perf_share = top_perf["Orders"] / perf["Orders"].sum() * 100

    # ---- Summary paragraph ----
    summary_box(
        f"<b>KPI overview:</b> Orders are delivered in <b>{avg_delivery_time:.1f} minutes</b> on "
        f"average. The delivery success rate is <b>{delivered_pct:.1f}%</b> and the cancellation "
        f"rate is <b>{cancellation_rate:.1f}%</b>. Customers give an average delivery rating of "
        f"<b>{avg_rating:.2f} out of 5</b>.",
        f"<b>Chart insights:</b> <b>{slow_city['City']}</b> is the slowest city with an average of "
        f"<b>{slow_city['Delivery_Time_Min']:.1f} minutes</b>, while <b>{fast_city['City']}</b> is the "
        f"fastest with <b>{fast_city['Delivery_Time_Min']:.1f} minutes</b>. The average delivery "
        f"distance is <b>{avg_distance:.1f} km</b>, and the link between distance and delivery time "
        f"{relation_text}. Most orders fall in the <b>{top_perf['Performance']}</b> category "
        f"(<b>{top_perf_share:.1f}%</b> of orders).",
    )

# TAB 3 - RESTAURANTS

with tab3:

    top_n = st.slider("How many restaurants to show?", 5, 20, 10)

    counts = filtered_df.groupby("Restaurant_Name").size()
    qualified = counts[counts >= 5].index
    q_df = filtered_df[filtered_df["Restaurant_Name"].isin(qualified)]

    # ---- Chart 1: Top by revenue ----
    top_rev = (
        filtered_df.groupby("Restaurant_Name")["Final_Amount"]
        .sum().sort_values(ascending=False).head(top_n).reset_index()
    )

    fig = px.bar(
        top_rev.sort_values("Final_Amount"), x="Final_Amount", y="Restaurant_Name",
        orientation="h", text="Final_Amount",
        color_discrete_sequence=[BLUE],
        title=f"Top {top_n} Restaurants by Revenue",
        labels={"Final_Amount": "Revenue (₹)", "Restaurant_Name": "Restaurant"},
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis_title="")
    show(fig)

    best_rest = top_rev.iloc[0]
    top_rev_share = top_rev["Final_Amount"].sum() / total_revenue * 100

    if len(qualified) == 0:
        st.info("Not enough data: no restaurant has 5 or more orders in this selection.")
        rating_text = "No restaurant has 5 or more orders in the current selection, so rating and cancellation comparisons are not available."
    else:
        # ---- Chart 2: Top rated ----
        top_rated = (
            q_df.groupby("Restaurant_Name")["Restaurant_Rating"]
            .mean().sort_values(ascending=False).head(top_n).reset_index()
        )

        fig = px.bar(
            top_rated.sort_values("Restaurant_Rating"), x="Restaurant_Rating", y="Restaurant_Name",
            orientation="h", text="Restaurant_Rating",
            color_discrete_sequence=["#2CA02C"],
            title=f"Top {top_n} Rated Restaurants (5+ orders)",
            labels={"Restaurant_Rating": "Avg Rating", "Restaurant_Name": "Restaurant"},
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(yaxis_title="")
        show(fig)

        tr = top_rated.iloc[0]

        # ---- Chart 3: Highest cancellation rate ----
        cancel = (
            q_df.groupby("Restaurant_Name")["Order_Status"]
            .apply(lambda s: (s == "Cancelled").mean() * 100)
            .sort_values(ascending=False).head(top_n).reset_index()
        )
        cancel.columns = ["Restaurant_Name", "Cancel_Pct"]

        fig = px.bar(
            cancel.sort_values("Cancel_Pct"), x="Cancel_Pct", y="Restaurant_Name",
            orientation="h", text="Cancel_Pct",
            color_discrete_sequence=["#D62728"],
            title=f"Top {top_n} Restaurants by Cancellation Rate (5+ orders)",
            labels={"Cancel_Pct": "Cancellation Rate (%)", "Restaurant_Name": "Restaurant"},
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(yaxis_title="")
        show(fig)

        wc = cancel.iloc[0]

        rating_text = (
            f"Among restaurants with at least 5 orders, <b>{tr['Restaurant_Name']}</b> has the "
            f"highest average rating (<b>{tr['Restaurant_Rating']:.2f}</b>), while "
            f"<b>{wc['Restaurant_Name']}</b> has the highest cancellation rate "
            f"(<b>{wc['Cancel_Pct']:.1f}%</b>) and needs a closer look."
        )

    # ---- Summary paragraph ----
    summary_box(
        f"<b>KPI overview:</b> The selection covers <b>{counts.shape[0]:,}</b> restaurants and "
        f"<b>{total_orders:,}</b> orders. The average order value is <b>₹{avg_order_value:,.0f}</b>, "
        f"the profit margin is <b>{avg_profit_margin:.1f}%</b> and the overall cancellation rate is "
        f"<b>{cancellation_rate:.1f}%</b>.",
        f"<b>Chart insights:</b> <b>{best_rest['Restaurant_Name']}</b> is the highest-revenue "
        f"restaurant with <b>₹{best_rest['Final_Amount']:,.0f}</b>, and the top {top_n} restaurants "
        f"together bring <b>{top_rev_share:.1f}%</b> of total revenue. {rating_text}",
    )

# TAB 4 - OPERATIONS

with tab4:

    # ---- Chart 1: Payment mode ----
    pay = filtered_df["Payment_Mode"].value_counts().reset_index()
    pay.columns = ["Payment_Mode", "Orders"]

    fig = px.pie(
        pay, names="Payment_Mode", values="Orders", hole=0.45,
        color_discrete_sequence=COLORS,
        title="Payment Mode Preferences",
    )
    fig.update_traces(textinfo="label+percent+value", textfont_size=14)
    show(fig)

    top_pay = pay.iloc[0]
    top_pay_share = top_pay["Orders"] / pay["Orders"].sum() * 100

    # ---- Chart 2: Cancellation reasons ----
    cancelled_only = filtered_df[filtered_df["Order_Status"] == "Cancelled"]

    if cancelled_only.empty:
        st.info("No cancelled orders in the current selection.")
        reason_text = "There are no cancelled orders in the current selection."
    else:
        reasons = cancelled_only["Cancellation_Reason"].value_counts().reset_index()
        reasons.columns = ["Reason", "Orders"]

        fig = px.bar(
            reasons, x="Reason", y="Orders", text="Orders",
            color_discrete_sequence=["#D62728"],
            title="Why Orders Get Cancelled",
        )
        fig.update_traces(textposition="outside")
        show(fig)

        top_reason = reasons.iloc[0]
        reason_text = (
            f"The most common cancellation reason is <b>{top_reason['Reason']}</b>, which causes "
            f"<b>{top_reason['Orders'] / reasons['Orders'].sum() * 100:.1f}%</b> of all cancellations."
        )

    # ---- Chart 3: Peak vs non-peak by cuisine ----
    peak_data = filtered_df.copy()
    peak_data["Peak_Label"] = np.where(peak_data["Peak_Hour"] == 1, "Peak Hour", "Non-Peak Hour")

    peak_cuisine = (
        peak_data.groupby(["Cuisine_Type", "Peak_Label"]).size().reset_index(name="Orders")
    )

    fig = px.bar(
        peak_cuisine, x="Cuisine_Type", y="Orders", color="Peak_Label", text="Orders",
        barmode="group", color_discrete_sequence=[BLUE, "#FF7F0E"],
        title="Peak vs Non-Peak Orders by Cuisine",
    )
    fig.update_traces(textposition="outside")
    show(fig)

    peak_pct = peak_data["Peak_Label"].eq("Peak Hour").mean() * 100
    peak_only = peak_data[peak_data["Peak_Label"] == "Peak Hour"].groupby("Cuisine_Type").size()
    peak_top_name = peak_only.idxmax() if not peak_only.empty else "not available"

    # ---- Summary paragraph ----
    summary_box(
        f"<b>KPI overview:</b> Out of <b>{total_orders:,}</b> orders, <b>{delivered_pct:.1f}%</b> "
        f"were delivered successfully and <b>{cancellation_rate:.1f}%</b> were cancelled. The average "
        f"delivery time is <b>{avg_delivery_time:.1f} minutes</b>.",
        f"<b>Chart insights:</b> <b>{top_pay['Payment_Mode']}</b> is the most used payment mode "
        f"(<b>{top_pay_share:.1f}%</b> of orders). {reason_text} About <b>{peak_pct:.1f}%</b> of "
        f"orders are placed in peak hours, and <b>{peak_top_name}</b> is the most ordered cuisine "
        f"during those hours.",
    )

# FOOTER

st.divider()
st.caption(
    "Built with Python · Pandas · NumPy · Plotly · Streamlit "
    "| Use the sidebar filters to explore different cities, cuisines and dates."
)