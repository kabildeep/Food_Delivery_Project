# 🍔 Online Food Delivery Analysis: Data-Driven Business Insights

A beginner-friendly, end-to-end data analytics project on a 100,000-row
online food delivery dataset — covering data cleaning, SQL storage,
exploratory data analysis, and an interactive Streamlit dashboard.

## 📁 Project Structure

```
Food_Delivery_Project/
├── data/
│   ├── food_delivery.csv            # Raw dataset (100,000 rows, 25 columns)
│   └── food_delivery_cleaned.csv    # Cleaned dataset (created by data_cleaning.py)
├── notebooks/
│   └── food_delivery_analysis.ipynb # Full EDA notebook with charts & insights
├── python/
│   ├── data_cleaning.py             # Cleans the raw data
│   └── upload_to_mysql.py           # Uploads cleaned data into MySQL
├── sql/
│   └── food_delivery_analysis.sql   # Table schema + business analysis queries
├── app.py                           # Streamlit interactive dashboard
├── requirements.txt                 # Python packages needed
├── .env.example                     # Template for your MySQL credentials
├── .gitignore
└── README.md
```

## 🧾 Dataset Overview

100,000 online food delivery orders with 25 raw columns covering
customer details, order information, restaurant attributes, delivery
performance and financial metrics.

## 🚀 How to Run This Project (step by step)

### 1. Set up your environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 2. Clean the data
```bash
python python/data_cleaning.py
```
This reads `data/food_delivery.csv` and creates
`data/food_delivery_cleaned.csv`.

### 3. (Optional) Load the data into MySQL
1. Make sure MySQL Server is running.
2. Copy `.env.example` to `.env` and fill in your real MySQL username/password.
3. Run the `CREATE DATABASE` / `CREATE TABLE` statements in
   `sql/food_delivery_analysis.sql` once (Part 1 of that file).
4. Run:
   ```bash
   python python/upload_to_mysql.py
   ```
5. Explore the business questions in Part 2 of
   `sql/food_delivery_analysis.sql` using MySQL Workbench or the CLI.

### 4. Explore the data in Jupyter
```bash
jupyter notebook notebooks/food_delivery_analysis.ipynb
```
Run every cell from top to bottom.

### 5. Launch the interactive dashboard
```bash
streamlit run app.py
```
This opens a browser tab with KPIs, filters (city, cuisine, order
status, date range) and charts.

## 🧹 Data Cleaning Summary

| Issue Found | How It Was Fixed |
|---|---|
| Missing numeric values (age, delivery time, distance, order value) | Filled with the column **median** |
| Missing discount | Filled with **0** (assume no discount) |
| Missing categorical values (gender, city, area, cuisine, payment mode) | Filled with the column **mode** (most common value) |
| Missing/incorrect `Final_Amount` | Recalculated as `Order_Value - Discount_Applied`, floored at 0 |
| Ratings above 5 | Capped at 5 (and floored at 1) |
| Negative profit margin | Floored at 0 |
| Cancelled orders with a delivery rating | Rating cleared (a cancelled order was never delivered) |
| Delivered orders with a cancellation reason | Reason set to "Not Cancelled" |
| Cancelled orders with a *missing* reason (~40% of cancellations) | Labeled "Unknown" — kept separate from "Not Cancelled" so it's clear the order *was* cancelled, the reason just wasn't logged |
| Extreme outliers (delivery time, distance, order value) | Capped using the IQR method |
| `Order_Time` column (always "0:00", no useful information) | Dropped |
| Rows with missing order date | Dropped (can't do date-based analysis without one) |

## 🏗️ Derived (Feature-Engineered) Columns

- `Order_Month` — month name, for revenue trend analysis
- `Profit_Margin_Pct` — profit margin as a percentage
- `Delivery_Performance` — Fast (≤30 min) / Moderate (≤60 min) / Slow (>60 min)
- `Customer_Age_Group` — 18-25 / 26-35 / 36-45 / 46+

## 📊 Dashboard KPIs

Total Orders · Total Revenue · Average Order Value · Average Delivery
Time · Cancellation Rate · Average Delivery Rating · Average Profit
Margin %

## 🔍 Analytical Questions Answered

- Top-spending customers & order value by age group
- Weekend vs weekday ordering patterns
- Monthly revenue trend
- Impact of discounts on profit margin
- Highest-revenue cities & cuisines
- Average delivery time by city
- Distance vs delivery time relationship
- Delivery rating vs delivery speed
- Top-rated restaurants & highest cancellation-rate restaurants
- Cuisine-wise performance
- Peak-hour vs non-peak-hour demand
- Payment mode preferences
- Cancellation reason breakdown

## 🛠️ Tech Stack

Python (pandas, NumPy) · Matplotlib & Seaborn · MySQL & SQLAlchemy ·
Streamlit & Plotly · Jupyter Notebook

## 📌 Notes

- The dashboard reads directly from the cleaned CSV file, so it works
  even without MySQL set up. MySQL is there for anyone who wants to
  practice SQL querying on top of the same cleaned data.
- Re-run `python/data_cleaning.py` any time the raw CSV changes — it
  will regenerate `food_delivery_cleaned.csv` automatically.
