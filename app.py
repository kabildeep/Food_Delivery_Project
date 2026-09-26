
"""
Online Food Delivery Analysis - Interactive Streamlit Dashboard

Run:
    python -m streamlit run app.py
"""

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Food Delivery Analysis Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_csv(
        "data/food_delivery_cleaned.csv",
        parse_dates=["Order_Date"]
    )

    return data


df = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("🍔 Online Food Delivery Analysis Dashboard")

st.caption(
    "Interactive analysis of customer behaviour, revenue, "
    "delivery performance and restaurant operations."
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")


city_options = sorted(
    df["City"].dropna().unique()
)

cuisine_options = sorted(
    df["Cuisine_Type"].dropna().unique()
)

status_options = sorted(
    df["Order_Status"].dropna().unique()
)


selected_cities = st.sidebar.multiselect(
    "🏙️ City",
    city_options,
    default=city_options
)


selected_cuisines = st.sidebar.multiselect(
    "🍛 Cuisine Type",
    cuisine_options,
    default=cuisine_options
)


selected_status = st.sidebar.multiselect(
    "📦 Order Status",
    status_options,
    default=status_options
)


min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()


date_range = st.sidebar.date_input(
    "📅 Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df[
    df["City"].isin(selected_cities)
    & df["Cuisine_Type"].isin(selected_cuisines)
    & df["Order_Status"].isin(selected_status)
].copy()


if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])

    end_date = (
        pd.to_datetime(date_range[1])
        + pd.Timedelta(days=1)
    )

    filtered_df = filtered_df[
        (filtered_df["Order_Date"] >= start_date)
        & (filtered_df["Order_Date"] < end_date)
    ]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data matches the selected filters. "
        "Please widen your selection."
    )

    st.stop()


# ============================================================
# SIDEBAR SUMMARY
# ============================================================

st.sidebar.divider()

st.sidebar.metric(
    "Filtered Orders",
    f"{len(filtered_df):,}"
)

st.sidebar.metric(
    "Filtered Revenue",
    f"₹{filtered_df['Final_Amount'].sum():,.0f}"
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_orders = len(filtered_df)


total_revenue = (
    filtered_df["Final_Amount"].sum()
)


avg_order_value = (
    filtered_df["Final_Amount"].mean()
)


avg_delivery_time = (
    filtered_df["Delivery_Time_Min"].mean()
)


cancellation_rate = (
    filtered_df["Order_Status"]
    .eq("Cancelled")
    .mean()
    * 100
)


delivered_only = filtered_df[
    filtered_df["Order_Status"] == "Delivered"
]


avg_delivery_rating = (
    delivered_only["Delivery_Rating"].mean()
    if not delivered_only.empty
    else 0
)


avg_profit_margin = (
    filtered_df["Profit_Margin_Pct"].mean()
)


delivered_percentage = (
    filtered_df["Order_Status"]
    .eq("Delivered")
    .mean()
    * 100
)


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📊 Key Performance Indicators")


# ------------------------------------------------------------
# FIRST KPI ROW
# ------------------------------------------------------------

kpi_row1 = st.columns(4)


with kpi_row1[0]:

    st.metric(
        label="🛒 Total Orders",
        value=f"{total_orders:,}"
    )


with kpi_row1[1]:

    st.metric(
        label="💰 Total Revenue",
        value=f"₹{total_revenue:,.0f}"
    )


with kpi_row1[2]:

    st.metric(
        label="💵 Avg Order Value",
        value=f"₹{avg_order_value:,.0f}"
    )


with kpi_row1[3]:

    st.metric(
        label="🚚 Avg Delivery Time",
        value=f"{avg_delivery_time:.1f} min"
    )


# ------------------------------------------------------------
# SECOND KPI ROW
# ------------------------------------------------------------

kpi_row2 = st.columns(4)


with kpi_row2[0]:

    st.metric(
        label="❌ Cancellation Rate",
        value=f"{cancellation_rate:.1f}%"
    )


with kpi_row2[1]:

    st.metric(
        label="⭐ Avg Delivery Rating",
        value=f"{avg_delivery_rating:.2f} / 5"
    )


with kpi_row2[2]:

    st.metric(
        label="📈 Avg Profit Margin",
        value=f"{avg_profit_margin:.1f}%"
    )


with kpi_row2[3]:

    st.metric(
        label="✅ Delivery Success",
        value=f"{delivered_percentage:.1f}%"
    )


st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Revenue & Orders",
        "🚚 Delivery Performance",
        "🍽️ Restaurants",
        "⚙️ Operations",
    ]
)


# ============================================================
# TAB 1
# REVENUE & ORDERS
# ============================================================

with tab1:

    st.header("📈 Revenue & Order Analysis")


    # --------------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        month_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]


        monthly_rev = (
            filtered_df
            .groupby("Order_Month")["Final_Amount"]
            .sum()
            .reindex(month_order)
            .dropna()
            .reset_index()
        )


        fig = px.line(
            monthly_rev,
            x="Order_Month",
            y="Final_Amount",
            markers=True,
            text="Final_Amount",
            title="Monthly Revenue Trend",
        )


        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="top center",
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>Revenue: ₹%{y:,.0f}"
                "<extra></extra>"
            ),
        )


        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue (₹)",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # REVENUE BY CITY
    # --------------------------------------------------------

    with col2:

        city_rev = (
            filtered_df
            .groupby("City")["Final_Amount"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )


        fig = px.bar(
            city_rev,
            x="City",
            y="Final_Amount",
            text="Final_Amount",
            title="Revenue by City",
        )


        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # REVENUE BY CUISINE
    # --------------------------------------------------------

    col3, col4 = st.columns(2)


    with col3:

        cuisine_rev = (
            filtered_df
            .groupby("Cuisine_Type")["Final_Amount"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )


        fig = px.bar(
            cuisine_rev,
            x="Cuisine_Type",
            y="Final_Amount",
            text="Final_Amount",
            title="Revenue by Cuisine",
        )


        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # AOV BY AGE GROUP
    # --------------------------------------------------------

    with col4:

        age_val = (
            filtered_df
            .groupby(
                "Customer_Age_Group",
                observed=True
            )["Final_Amount"]
            .mean()
            .reset_index()
        )


        fig = px.bar(
            age_val,
            x="Customer_Age_Group",
            y="Final_Amount",
            text="Final_Amount",
            title="Average Order Value by Age Group",
        )


        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # WEEKEND VS WEEKDAY
    # --------------------------------------------------------

    day_data = filtered_df.copy()


    day_data["Day_Type"] = np.where(
        day_data["Order_Day"].isin(
            ["Saturday", "Sunday"]
        ),
        "Weekend",
        "Weekday",
    )


    day_summary = (
        day_data
        .groupby("Day_Type")
        .agg(
            Orders=("Order_ID", "count"),
            Avg_Order_Value=(
                "Final_Amount",
                "mean"
            ),
        )
        .reset_index()
    )


    col5, col6 = st.columns(2)


    with col5:

        fig = px.bar(
            day_summary,
            x="Day_Type",
            y="Orders",
            text="Orders",
            title="Orders: Weekend vs Weekday",
        )


        fig.update_traces(
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col6:

        fig = px.bar(
            day_summary,
            x="Day_Type",
            y="Avg_Order_Value",
            text="Avg_Order_Value",
            title="Average Order Value: Weekend vs Weekday",
        )


        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ORDER STATUS
    # --------------------------------------------------------

    status_data = (
        filtered_df["Order_Status"]
        .value_counts()
        .reset_index()
    )


    status_data.columns = [
        "Order_Status",
        "Orders"
    ]


    fig = px.pie(
        status_data,
        names="Order_Status",
        values="Orders",
        hole=0.45,
        title="Order Status Distribution",
    )


    fig.update_traces(
        textinfo="label+percent+value"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # MONTHLY ORDER VOLUME
    # --------------------------------------------------------

    monthly_orders = (
        filtered_df
        .groupby("Order_Month")
        .size()
        .reindex(month_order)
        .dropna()
        .reset_index(name="Orders")
    )


    fig = px.bar(
        monthly_orders,
        x="Order_Month",
        y="Orders",
        text="Orders",
        title="Monthly Order Volume",
    )


    fig.update_traces(
        textposition="outside"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TAB 1 INSIGHTS
    # --------------------------------------------------------

    st.subheader("💡 Revenue & Order Insights")


    top_city = (
        filtered_df
        .groupby("City")["Final_Amount"]
        .sum()
        .idxmax()
    )


    top_city_revenue = (
        filtered_df
        .groupby("City")["Final_Amount"]
        .sum()
        .max()
    )


    top_cuisine = (
        filtered_df
        .groupby("Cuisine_Type")["Final_Amount"]
        .sum()
        .idxmax()
    )


    weekend_orders = (
        day_data["Day_Type"]
        .eq("Weekend")
        .sum()
    )


    weekday_orders = (
        day_data["Day_Type"]
        .eq("Weekday")
        .sum()
    )


    highest_month = (
        monthly_rev.loc[
            monthly_rev["Final_Amount"].idxmax(),
            "Order_Month"
        ]
        if not monthly_rev.empty
        else "Not available"
    )


    st.info(
        f"""
**Revenue & Order Insights**

• **{top_city}** generates the highest revenue with
**₹{top_city_revenue:,.0f}**.

• **{top_cuisine}** is the highest-revenue cuisine
in the current selection.

• Total filtered orders: **{total_orders:,}**.

• Weekend orders: **{weekend_orders:,}**.

• Weekday orders: **{weekday_orders:,}**.

• Average order value: **₹{avg_order_value:,.0f}**.

• **{highest_month}** has the highest monthly revenue
in the current selection.
"""
    )


# ============================================================
# TAB 2
# DELIVERY PERFORMANCE
# ============================================================

with tab2:

    st.header("🚚 Delivery Performance Analysis")


    # --------------------------------------------------------
    # CITY DELIVERY TIME
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        city_time = (
            filtered_df
            .groupby("City")["Delivery_Time_Min"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )


        fig = px.bar(
            city_time,
            x="City",
            y="Delivery_Time_Min",
            text="Delivery_Time_Min",
            title="Average Delivery Time by City",
        )


        fig.update_traces(
            texttemplate="%{text:.1f} min",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # DISTANCE VS DELIVERY TIME
    # --------------------------------------------------------

    with col2:

        sample_df = filtered_df.sample(
            min(3000, len(filtered_df)),
            random_state=42,
        )


        fig = px.scatter(
            sample_df,
            x="Distance_km",
            y="Delivery_Time_Min",
            opacity=0.5,
            title="Distance vs Delivery Time",
            hover_data=[
                "City",
                "Delivery_Performance"
            ],
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # DELIVERY PERFORMANCE
    # --------------------------------------------------------

    col3, col4 = st.columns(2)


    with col3:

        perf_counts = (
            filtered_df["Delivery_Performance"]
            .value_counts()
            .reset_index()
        )


        perf_counts.columns = [
            "Delivery_Performance",
            "Orders"
        ]


        fig = px.pie(
            perf_counts,
            names="Delivery_Performance",
            values="Orders",
            hole=0.4,
            title="Delivery Performance Breakdown",
        )


        fig.update_traces(
            textinfo="label+percent+value"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # RATING BY PERFORMANCE
    # --------------------------------------------------------

    with col4:

        rating = (
            filtered_df
            .groupby(
                "Delivery_Performance"
            )["Delivery_Rating"]
            .mean()
            .reset_index()
        )


        fig = px.bar(
            rating,
            x="Delivery_Performance",
            y="Delivery_Rating",
            text="Delivery_Rating",
            title="Average Delivery Rating by Performance",
        )


        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # DELIVERY TIME DISTRIBUTION
    # --------------------------------------------------------

    fig = px.histogram(
        filtered_df,
        x="Delivery_Time_Min",
        nbins=30,
        title="Delivery Time Distribution",
        labels={
            "Delivery_Time_Min":
            "Delivery Time (Minutes)"
        },
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # DISTANCE BY CITY
    # --------------------------------------------------------

    distance_city = (
        filtered_df
        .groupby("City")["Distance_km"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )


    fig = px.bar(
        distance_city,
        x="City",
        y="Distance_km",
        text="Distance_km",
        title="Average Delivery Distance by City",
    )


    fig.update_traces(
        texttemplate="%{text:.1f} km",
        textposition="outside",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # DELIVERY TIME BY PERFORMANCE
    # --------------------------------------------------------

    performance_time = (
        filtered_df
        .groupby("Delivery_Performance")[
            "Delivery_Time_Min"
        ]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )


    fig = px.bar(
        performance_time,
        x="Delivery_Performance",
        y="Delivery_Time_Min",
        text="Delivery_Time_Min",
        title="Average Delivery Time by Performance",
    )


    fig.update_traces(
        texttemplate="%{text:.1f} min",
        textposition="outside",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TAB 2 INSIGHTS
    # --------------------------------------------------------

    st.subheader("💡 Delivery Insights")


    slowest_city = (
        filtered_df
        .groupby("City")["Delivery_Time_Min"]
        .mean()
        .idxmax()
    )


    slowest_time = (
        filtered_df
        .groupby("City")["Delivery_Time_Min"]
        .mean()
        .max()
    )


    fastest_city = (
        filtered_df
        .groupby("City")["Delivery_Time_Min"]
        .mean()
        .idxmin()
    )


    fastest_time = (
        filtered_df
        .groupby("City")["Delivery_Time_Min"]
        .mean()
        .min()
    )


    avg_distance = (
        filtered_df["Distance_km"].mean()
    )


    most_common_delivery_performance = (
        filtered_df["Delivery_Performance"]
        .value_counts()
        .idxmax()
    )


    st.info(
        f"""
**Delivery Performance Insights**

• **{slowest_city}** has the highest average
delivery time at **{slowest_time:.1f} minutes**.

• **{fastest_city}** has the lowest average delivery
time at **{fastest_time:.1f} minutes**.

• Average delivery distance is
**{avg_distance:.1f} km**.

• The most common delivery performance category is
**{most_common_delivery_performance}**.

• Overall average delivery time is
**{avg_delivery_time:.1f} minutes**.

• Average delivery rating is
**{avg_delivery_rating:.2f}/5**.
"""
    )


# ============================================================
# TAB 3
# RESTAURANTS
# ============================================================

with tab3:

    st.header("🍽️ Restaurant Performance Analysis")


    restaurant_counts = (
        filtered_df
        .groupby("Restaurant_Name")
        .size()
    )


    qualified = restaurant_counts[
        restaurant_counts >= 5
    ].index


    # --------------------------------------------------------
    # TOP RATED + CANCELLATION RATE
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        top_rated = (
            filtered_df[
                filtered_df["Restaurant_Name"]
                .isin(qualified)
            ]
            .groupby("Restaurant_Name")[
                "Restaurant_Rating"
            ]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )


        fig = px.bar(
            top_rated,
            x="Restaurant_Rating",
            y="Restaurant_Name",
            orientation="h",
            text="Restaurant_Rating",
            title="Top 10 Rated Restaurants (5+ Orders)",
        )


        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        cancel_rate = (
            filtered_df[
                filtered_df["Restaurant_Name"]
                .isin(qualified)
            ]
            .groupby("Restaurant_Name")[
                "Order_Status"
            ]
            .apply(
                lambda s:
                (s == "Cancelled").mean() * 100
            )
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )


        cancel_rate.columns = [
            "Restaurant_Name",
            "Cancellation_Rate_Pct"
        ]


        fig = px.bar(
            cancel_rate,
            x="Cancellation_Rate_Pct",
            y="Restaurant_Name",
            orientation="h",
            text="Cancellation_Rate_Pct",
            title="Top 10 Restaurants by Cancellation Rate",
        )


        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # RESTAURANT REVENUE
    # --------------------------------------------------------

    restaurant_revenue = (
        filtered_df
        .groupby("Restaurant_Name")[
            "Final_Amount"
        ]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )


    fig = px.bar(
        restaurant_revenue,
        x="Final_Amount",
        y="Restaurant_Name",
        orientation="h",
        text="Final_Amount",
        title="Top 10 Restaurants by Revenue",
    )


    fig.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RESTAURANT ORDER VOLUME
    # --------------------------------------------------------

    restaurant_orders = (
        filtered_df
        .groupby("Restaurant_Name")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="Orders")
    )


    fig = px.bar(
        restaurant_orders,
        x="Orders",
        y="Restaurant_Name",
        orientation="h",
        text="Orders",
        title="Top 10 Restaurants by Order Volume",
    )


    fig.update_traces(
        textposition="outside"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RESTAURANT RATING VS REVENUE
    # --------------------------------------------------------

    restaurant_analysis = (
        filtered_df
        .groupby("Restaurant_Name")
        .agg(
            Revenue=("Final_Amount", "sum"),
            Rating=("Restaurant_Rating", "mean"),
            Orders=("Order_ID", "count"),
        )
        .reset_index()
    )


    restaurant_analysis = restaurant_analysis[
        restaurant_analysis["Orders"] >= 5
    ]


    fig = px.scatter(
        restaurant_analysis,
        x="Rating",
        y="Revenue",
        size="Orders",
        hover_name="Restaurant_Name",
        title="Restaurant Rating vs Revenue",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RESTAURANT AVERAGE ORDER VALUE
    # --------------------------------------------------------

    restaurant_aov = (
        filtered_df
        .groupby("Restaurant_Name")
        .agg(
            Avg_Order_Value=(
                "Final_Amount",
                "mean"
            ),
            Orders=("Order_ID", "count")
        )
        .reset_index()
    )


    restaurant_aov = restaurant_aov[
        restaurant_aov["Orders"] >= 5
    ]


    restaurant_aov = (
        restaurant_aov
        .sort_values(
            "Avg_Order_Value",
            ascending=False
        )
        .head(10)
    )


    fig = px.bar(
        restaurant_aov,
        x="Avg_Order_Value",
        y="Restaurant_Name",
        orientation="h",
        text="Avg_Order_Value",
        title="Top 10 Restaurants by Average Order Value (5+ Orders)",
    )


    fig.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RESTAURANT INSIGHTS
    # --------------------------------------------------------

    st.subheader("💡 Restaurant Insights")


    top_revenue_restaurant = (
        filtered_df
        .groupby("Restaurant_Name")[
            "Final_Amount"
        ]
        .sum()
        .idxmax()
    )


    top_order_restaurant = (
        filtered_df
        .groupby("Restaurant_Name")
        .size()
        .idxmax()
    )


    if len(qualified) > 0:

        qualified_data = filtered_df[
            filtered_df["Restaurant_Name"]
            .isin(qualified)
        ]


        top_rating_restaurant = (
            qualified_data
            .groupby("Restaurant_Name")[
                "Restaurant_Rating"
            ]
            .mean()
            .idxmax()
        )


        highest_cancel_restaurant = (
            qualified_data
            .groupby("Restaurant_Name")[
                "Order_Status"
            ]
            .apply(
                lambda s:
                (s == "Cancelled").mean() * 100
            )
            .idxmax()
        )


    else:

        top_rating_restaurant = "Not enough data"

        highest_cancel_restaurant = "Not enough data"


    st.info(
        f"""
**Restaurant Performance Insights**

• **{top_revenue_restaurant}** generates the highest
restaurant revenue.

• **{top_order_restaurant}** has the highest number
of orders.

• Among restaurants with at least 5 orders,
**{top_rating_restaurant}** has the highest average rating.

• **{highest_cancel_restaurant}** has the highest
cancellation rate among qualified restaurants.

• Restaurant rating and cancellation comparisons use
a minimum threshold of **5 orders**.
"""
    )


# ============================================================
# TAB 4
# OPERATIONS
# ============================================================

with tab4:

    st.header("⚙️ Operations Analysis")


    # --------------------------------------------------------
    # PREPARE PEAK HOUR DATA
    # --------------------------------------------------------

    peak_data = filtered_df.copy()


    peak_data["Peak_Hour_Label"] = np.where(
        peak_data["Peak_Hour"] == 1,
        "Peak Hour",
        "Non-Peak Hour",
    )


    # --------------------------------------------------------
    # PEAK HOUR + PAYMENT MODE
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        peak_counts = (
            peak_data["Peak_Hour_Label"]
            .value_counts()
            .reset_index()
        )


        peak_counts.columns = [
            "Peak_Hour",
            "Orders"
        ]


        fig = px.bar(
            peak_counts,
            x="Peak_Hour",
            y="Orders",
            text="Orders",
            title="Peak Hour vs Non-Peak Hour",
        )


        fig.update_traces(
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        payment_counts = (
            filtered_df["Payment_Mode"]
            .value_counts()
            .reset_index()
        )


        payment_counts.columns = [
            "Payment_Mode",
            "Orders"
        ]


        fig = px.pie(
            payment_counts,
            names="Payment_Mode",
            values="Orders",
            hole=0.4,
            title="Payment Mode Preferences",
        )


        fig.update_traces(
            textinfo="label+percent+value"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # CANCELLATION REASONS
    # --------------------------------------------------------

    cancelled_only = filtered_df[
        filtered_df["Order_Status"] == "Cancelled"
    ]


    if not cancelled_only.empty:

        reason_counts = (
            cancelled_only[
                "Cancellation_Reason"
            ]
            .value_counts()
            .reset_index()
        )


        reason_counts.columns = [
            "Cancellation_Reason",
            "Orders"
        ]


        fig = px.bar(
            reason_counts,
            x="Cancellation_Reason",
            y="Orders",
            text="Orders",
            title="Cancellation Reasons",
        )


        fig.update_traces(
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ORDER STATUS BY CITY
    # --------------------------------------------------------

    status_city = (
        filtered_df
        .groupby(
            ["City", "Order_Status"]
        )
        .size()
        .reset_index(name="Orders")
    )


    fig = px.bar(
        status_city,
        x="City",
        y="Orders",
        color="Order_Status",
        barmode="group",
        title="Order Status Distribution by City",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # PAYMENT MODE BY CUISINE
    # --------------------------------------------------------

    payment_cuisine = (
        filtered_df
        .groupby(
            ["Cuisine_Type", "Payment_Mode"]
        )
        .size()
        .reset_index(name="Orders")
    )


    fig = px.bar(
        payment_cuisine,
        x="Cuisine_Type",
        y="Orders",
        color="Payment_Mode",
        barmode="stack",
        title="Payment Mode by Cuisine",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # PEAK HOUR BY CUISINE
    # --------------------------------------------------------

    peak_cuisine = (
        peak_data
        .groupby(
            ["Cuisine_Type", "Peak_Hour_Label"]
        )
        .size()
        .reset_index(name="Orders")
    )


    fig = px.bar(
        peak_cuisine,
        x="Cuisine_Type",
        y="Orders",
        color="Peak_Hour_Label",
        barmode="group",
        title="Peak Hour Orders by Cuisine",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ORDER STATUS BY PAYMENT MODE
    # --------------------------------------------------------

    status_payment = (
        filtered_df
        .groupby(
            ["Payment_Mode", "Order_Status"]
        )
        .size()
        .reset_index(name="Orders")
    )


    fig = px.bar(
        status_payment,
        x="Payment_Mode",
        y="Orders",
        color="Order_Status",
        barmode="stack",
        title="Order Status by Payment Mode",
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # OPERATIONS INSIGHTS
    # --------------------------------------------------------

    st.subheader("💡 Operations Insights")


    peak_percentage = (
        filtered_df["Peak_Hour"]
        .eq(1)
        .mean()
        * 100
    )


    most_used_payment = (
        filtered_df["Payment_Mode"]
        .value_counts()
        .idxmax()
    )


    most_common_status = (
        filtered_df["Order_Status"]
        .value_counts()
        .idxmax()
    )


    if not cancelled_only.empty:

        most_common_reason = (
            cancelled_only[
                "Cancellation_Reason"
            ]
            .value_counts()
            .idxmax()
        )

    else:

        most_common_reason = "No cancelled orders"


    st.info(
        f"""
**Operations Insights**

• **{peak_percentage:.1f}%** of filtered orders
occurred during the defined peak hours.

• **{most_used_payment}** is the most frequently used
payment mode.

• **{most_common_status}** is the most common order status.

• Cancellation rate is **{cancellation_rate:.1f}%**.

• Most common cancellation reason:
**{most_common_reason}**.

• Results change dynamically when the sidebar
filters are modified.
"""
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    "Built with Python · Pandas · NumPy · Plotly · Streamlit "
    "| Interactive Food Delivery Analysis Dashboard"
)


st.caption(
    "Use the sidebar filters to dynamically analyse different "
    "cities, cuisines, order statuses and date ranges."
)

