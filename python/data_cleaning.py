import pandas as pd
import numpy as np


RAW_FILE = "data/food_delivery.csv"
CLEANED_FILE = "data/food_delivery_cleaned.csv"


def load_data(path):
    print("Step 1: Loading raw data...")
    df = pd.read_csv(path)
    print(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
    return df


def fix_missing_values(df):
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
    df = df.dropna(subset=["Order_Date"])

    df = df.drop(columns=["Order_Time"])


    print("Missing values handled.")
    return df


def fix_final_amount(df):
   
    print("Step 3: Recalculating Final_Amount (Order_Value - Discount)...")
    df["Final_Amount"] = df["Order_Value"] - df["Discount_Applied"]

    # A final amount should never be negative -> floor it at 0
    df["Final_Amount"] = df["Final_Amount"].clip(lower=0)
    return df


def fix_invalid_values(df):
    print("Step 4: Fixing invalid / out-of-range values...")

    # Ratings must be between 1 and 5. Anything above 5 gets capped at 5.
    df["Restaurant_Rating"] = df["Restaurant_Rating"].clip(upper=5, lower=1)
    df["Delivery_Rating"] = df["Delivery_Rating"].clip(upper=5, lower=1)

    # Profit margin should not be negative for this business model ->
    # floor it at 0
    df["Profit_Margin"] = df["Profit_Margin"].clip(lower=0)

    return df


def fix_logical_consistency(df):
    print("Step 5: Fixing logical inconsistencies...")

    # A CANCELLED order should NOT have a delivery rating
    df.loc[df["Order_Status"] == "Cancelled", "Delivery_Rating"] = np.nan

    # A DELIVERED order should NOT have a cancellation reason
    df.loc[df["Order_Status"] == "Delivered", "Cancellation_Reason"] = "Not Cancelled"

   
    is_cancelled_missing_reason = (
        (df["Order_Status"] == "Cancelled") & (df["Cancellation_Reason"].isna())
    )
    df.loc[is_cancelled_missing_reason, "Cancellation_Reason"] = "Unknown"

    median_rating = df.loc[df["Order_Status"] == "Delivered", "Delivery_Rating"].median()
    df["Delivery_Rating"] = df["Delivery_Rating"].fillna(median_rating)

    return df


def handle_outliers(df):
    
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

    print("New columns added: Order_Month, Profit_Margin_Pct, "
          "Delivery_Performance, Customer_Age_Group")
    return df


def clean_data():
    
    df = load_data(RAW_FILE)
    df = fix_missing_values(df)
    df = fix_final_amount(df)
    df = fix_invalid_values(df)
    df = fix_logical_consistency(df)
    df = handle_outliers(df)
    df = add_derived_columns(df)

    print(f"Step 8: Saving cleaned data to {CLEANED_FILE} ...")
    df.to_csv(CLEANED_FILE, index=False)
    print(f"Done! Final cleaned dataset has {df.shape[0]} rows "
          f"and {df.shape[1]} columns.")
    return df


if __name__ == "__main__":
    clean_data()
