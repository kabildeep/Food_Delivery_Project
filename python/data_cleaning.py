"""
data_cleaning.py
------------------------------------------------------------
Online Food Delivery Analysis - Data Cleaning & Preprocessing
------------------------------------------------------------
What this script does (in plain steps):
 1. Loads the raw CSV file (data/food_delivery.csv)
 2. Fixes missing values (using mean / median / mode)
 3. Fixes invalid values (ratings above 5, negative amounts, etc.)
 4. Fixes logical mistakes (e.g. a cancelled order should not have a
    delivery rating, a delivered order should not have a cancellation
    reason)
 5. Creates a few new "derived" columns that make analysis easier
 6. Saves the cleaned data to data/food_delivery_cleaned.csv

You can just run this file from the terminal:
    python python/data_cleaning.py
"""

import pandas as pd
import numpy as np

# ----------------------------------------------------------------
# STEP 0: File paths (edit these if your folders are named differently)
# ----------------------------------------------------------------
RAW_FILE = "data/food_delivery.csv"
CLEANED_FILE = "data/food_delivery_cleaned.csv"


def load_data(path):
    """Read the raw CSV file into a pandas DataFrame."""
    print("Step 1: Loading raw data...")
    df = pd.read_csv(path)
    print(f"   Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
    return df


def fix_missing_values(df):
    """Fill in missing (NaN) values with sensible defaults."""
    print("Step 2: Handling missing values...")

    # --- Numeric columns -> fill with the MEDIAN of that column ---
    numeric_cols_median = [
        "Customer_Age",
        "Delivery_Time_Min",
        "Distance_km",
        "Order_Value",
    ]
    for col in numeric_cols_median:
        median_value = df[col].median()
        df[col] = df[col].fillna(median_value)

    # --- Discount: if missing, assume no discount was given (0) ---
    df["Discount_Applied"] = df["Discount_Applied"].fillna(0)

    # --- Text / category columns -> fill with the MODE (most common value) ---
    categorical_cols_mode = [
        "Customer_Gender",
        "City",
        "Area",
        "Cuisine_Type",
        "Payment_Mode",
    ]
    for col in categorical_cols_mode:
        mode_value = df[col].mode(dropna=True)[0]
        df[col] = df[col].fillna(mode_value)

    # --- Peak_Hour: fill missing with the most common value (True/False) ---
    mode_peak = df["Peak_Hour"].mode(dropna=True)[0]
    df["Peak_Hour"] = df["Peak_Hour"].fillna(mode_peak)

    # --- Order_Date: drop rows where the date itself is missing ---
    # (Without a date we cannot do any time-based analysis for that row)
    df = df.dropna(subset=["Order_Date"])

    # --- Order_Time: every value in this column is "0:00", so it carries
    # no real information. We drop it instead of trying to fill it. ---
    df = df.drop(columns=["Order_Time"])

    # NOTE: Cancellation_Reason missing values are handled later in
    # fix_logical_consistency(), because a missing reason means something
    # different depending on whether the order was cancelled or delivered.

    print("   Missing values handled.")
    return df


def fix_final_amount(df):
    """
    Final_Amount should always equal Order_Value - Discount_Applied.
    We recalculate it everywhere to fix missing values AND negative
    values in one go (this also fixes rows with wrong stored values).
    """
    print("Step 3: Recalculating Final_Amount (Order_Value - Discount)...")
    df["Final_Amount"] = df["Order_Value"] - df["Discount_Applied"]

    # A final amount should never be negative -> floor it at 0
    df["Final_Amount"] = df["Final_Amount"].clip(lower=0)
    return df


def fix_invalid_values(df):
    """Correct values that break real-world business rules."""
    print("Step 4: Fixing invalid / out-of-range values...")

    # Ratings must be between 1 and 5. Anything above 5 gets capped at 5.
    df["Restaurant_Rating"] = df["Restaurant_Rating"].clip(upper=5, lower=1)
    df["Delivery_Rating"] = df["Delivery_Rating"].clip(upper=5, lower=1)

    # Profit margin should not be negative for this business model ->
    # floor it at 0
    df["Profit_Margin"] = df["Profit_Margin"].clip(lower=0)

    return df


def fix_logical_consistency(df):
    """Fix rows where two columns contradict each other."""
    print("Step 5: Fixing logical inconsistencies...")

    # A CANCELLED order should NOT have a delivery rating
    df.loc[df["Order_Status"] == "Cancelled", "Delivery_Rating"] = np.nan

    # A DELIVERED order should NOT have a cancellation reason
    df.loc[df["Order_Status"] == "Delivered", "Cancellation_Reason"] = "Not Cancelled"

    # A CANCELLED order that is genuinely missing a reason gets labeled
    # "Unknown" (NOT "Not Cancelled" - it WAS cancelled, we just don't
    # know why).
    is_cancelled_missing_reason = (
        (df["Order_Status"] == "Cancelled") & (df["Cancellation_Reason"].isna())
    )
    df.loc[is_cancelled_missing_reason, "Cancellation_Reason"] = "Unknown"

    # Now fill the Delivery_Rating we just cleared (only for Delivered
    # orders that were genuinely missing a rating) using the median
    median_rating = df.loc[df["Order_Status"] == "Delivered", "Delivery_Rating"].median()
    df["Delivery_Rating"] = df["Delivery_Rating"].fillna(median_rating)

    return df


def handle_outliers(df):
    """
    Cap extreme outliers in Delivery_Time_Min and Distance_km using the
    IQR (Inter-Quartile Range) method, a simple and common technique.
    """
    print("Step 6: Capping outliers (delivery time & distance)...")

    for col in ["Delivery_Time_Min", "Distance_km", "Order_Value"]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

    return df


def add_derived_columns(df):
    """Create new, easy-to-analyze columns (feature engineering)."""
    print("Step 7: Creating derived columns...")

    # Convert Order_Date text into a real date type
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Order_Month"] = df["Order_Date"].dt.month_name()

    # Profit margin as a percentage (easier to read on a dashboard)
    df["Profit_Margin_Pct"] = (df["Profit_Margin"] * 100).round(2)

    # Delivery performance category, based on delivery time
    def delivery_category(minutes):
        if minutes <= 30:
            return "Fast"
        elif minutes <= 60:
            return "Moderate"
        else:
            return "Slow"

    df["Delivery_Performance"] = df["Delivery_Time_Min"].apply(delivery_category)

    # Customer age groups
    bins = [0, 25, 35, 45, 100]
    labels = ["18-25", "26-35", "36-45", "46+"]
    df["Customer_Age_Group"] = pd.cut(df["Customer_Age"], bins=bins, labels=labels)

    print("   New columns added: Order_Month, Profit_Margin_Pct, "
          "Delivery_Performance, Customer_Age_Group")
    return df


def clean_data():
    """Run every cleaning step, in order, and save the result."""
    df = load_data(RAW_FILE)
    df = fix_missing_values(df)
    df = fix_final_amount(df)
    df = fix_invalid_values(df)
    df = fix_logical_consistency(df)
    df = handle_outliers(df)
    df = add_derived_columns(df)

    print(f"Step 8: Saving cleaned data to {CLEANED_FILE} ...")
    df.to_csv(CLEANED_FILE, index=False)
    print(f"   Done! Final cleaned dataset has {df.shape[0]} rows "
          f"and {df.shape[1]} columns.")
    return df


if __name__ == "__main__":
    clean_data()
