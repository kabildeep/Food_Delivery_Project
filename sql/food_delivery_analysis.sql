-- ============================================================
-- Online Food Delivery Analysis - SQL Database
-- ============================================================
-- This file has two parts:
--   PART 1: Create the database + table (run this once)
--   PART 2: Business analysis queries (run these anytime after
--            the cleaned data has been uploaded with
--            python/upload_to_mysql.py)
-- ============================================================


-- ============================================================
-- PART 1: DATABASE & TABLE CREATION
-- ============================================================

CREATE DATABASE IF NOT EXISTS food_delivery_db;
USE food_delivery_db;

DROP TABLE IF EXISTS food_delivery_cleaned;

CREATE TABLE food_delivery_cleaned (
    Order_ID              VARCHAR(20) PRIMARY KEY,
    Customer_ID            VARCHAR(20),
    Customer_Age           INT,
    Customer_Gender        VARCHAR(10),
    City                    VARCHAR(50),
    Area                    VARCHAR(50),
    Restaurant_ID           VARCHAR(20),
    Restaurant_Name         VARCHAR(100),
    Cuisine_Type            VARCHAR(50),
    Order_Date              DATE,
    Delivery_Time_Min       FLOAT,
    Distance_km             FLOAT,
    Order_Value             FLOAT,
    Discount_Applied        FLOAT,
    Final_Amount            FLOAT,
    Payment_Mode            VARCHAR(20),
    Order_Status            VARCHAR(20),
    Cancellation_Reason     VARCHAR(50),
    Delivery_Partner_ID     VARCHAR(20),
    Delivery_Rating         FLOAT,
    Restaurant_Rating       FLOAT,
    Order_Day               VARCHAR(10),
    Peak_Hour               BOOLEAN,
    Profit_Margin           FLOAT,
    Order_Month             VARCHAR(20),
    Profit_Margin_Pct       FLOAT,
    Delivery_Performance    VARCHAR(20),
    Customer_Age_Group      VARCHAR(20)
);

-- NOTE: You do not need to manually INSERT data here.
-- Run python/upload_to_mysql.py, which reads
-- data/food_delivery_cleaned.csv and loads it into this table
-- automatically using SQLAlchemy + pandas.


-- ============================================================
-- PART 2: BUSINESS ANALYSIS QUERIES
-- ============================================================

-- ---------- A. CUSTOMER & ORDER ANALYSIS ----------

-- A1. Top 10 highest-spending customers
SELECT Customer_ID,
       COUNT(*)            AS Total_Orders,
       SUM(Final_Amount)   AS Total_Spent
FROM food_delivery_cleaned
GROUP BY Customer_ID
ORDER BY Total_Spent DESC
LIMIT 10;

-- A2. Average order value by customer age group
SELECT Customer_Age_Group,
       ROUND(AVG(Final_Amount), 2) AS Avg_Order_Value,
       COUNT(*)                    AS Total_Orders
FROM food_delivery_cleaned
GROUP BY Customer_Age_Group
ORDER BY Customer_Age_Group;

-- A3. Weekend vs weekday order patterns
SELECT Order_Day,
       COUNT(*)                    AS Total_Orders,
       ROUND(AVG(Final_Amount), 2) AS Avg_Order_Value
FROM food_delivery_cleaned
GROUP BY Order_Day;


-- ---------- B. REVENUE & PROFIT ANALYSIS ----------

-- B1. Monthly revenue trend
SELECT Order_Month,
       ROUND(SUM(Final_Amount), 2) AS Monthly_Revenue,
       COUNT(*)                    AS Total_Orders
FROM food_delivery_cleaned
GROUP BY Order_Month
ORDER BY Monthly_Revenue DESC;

-- B2. Impact of discounts on profit margin
SELECT
    CASE
        WHEN Discount_Applied = 0 THEN 'No Discount'
        WHEN Discount_Applied <= 50 THEN 'Low Discount (<=50)'
        ELSE 'High Discount (>50)'
    END AS Discount_Band,
    ROUND(AVG(Profit_Margin_Pct), 2) AS Avg_Profit_Margin_Pct,
    COUNT(*)                         AS Total_Orders
FROM food_delivery_cleaned
GROUP BY Discount_Band;

-- B3. Top 5 highest-revenue cities
SELECT City,
       ROUND(SUM(Final_Amount), 2) AS Total_Revenue
FROM food_delivery_cleaned
GROUP BY City
ORDER BY Total_Revenue DESC
LIMIT 5;

-- B4. Top 5 highest-revenue cuisines
SELECT Cuisine_Type,
       ROUND(SUM(Final_Amount), 2) AS Total_Revenue
FROM food_delivery_cleaned
GROUP BY Cuisine_Type
ORDER BY Total_Revenue DESC
LIMIT 5;


-- ---------- C. DELIVERY PERFORMANCE ----------

-- C1. Average delivery time by city
SELECT City,
       ROUND(AVG(Delivery_Time_Min), 2) AS Avg_Delivery_Time_Min
FROM food_delivery_cleaned
GROUP BY City
ORDER BY Avg_Delivery_Time_Min DESC;

-- C2. Distance vs delivery time (grouped into distance bands)
SELECT
    CASE
        WHEN Distance_km <= 5  THEN '0-5 km'
        WHEN Distance_km <= 15 THEN '5-15 km'
        WHEN Distance_km <= 25 THEN '15-25 km'
        ELSE '25+ km'
    END AS Distance_Band,
    ROUND(AVG(Delivery_Time_Min), 2) AS Avg_Delivery_Time_Min,
    COUNT(*)                         AS Total_Orders
FROM food_delivery_cleaned
GROUP BY Distance_Band;

-- C3. Delivery rating vs delivery performance category
SELECT Delivery_Performance,
       ROUND(AVG(Delivery_Rating), 2) AS Avg_Delivery_Rating,
       COUNT(*)                       AS Total_Orders
FROM food_delivery_cleaned
WHERE Order_Status = 'Delivered'
GROUP BY Delivery_Performance;


-- ---------- D. RESTAURANT PERFORMANCE ----------

-- D1. Top 10 highest-rated restaurants (minimum 20 orders, to be fair)
SELECT Restaurant_Name,
       ROUND(AVG(Restaurant_Rating), 2) AS Avg_Rating,
       COUNT(*)                         AS Total_Orders
FROM food_delivery_cleaned
GROUP BY Restaurant_Name
HAVING COUNT(*) >= 20
ORDER BY Avg_Rating DESC
LIMIT 10;

-- D2. Cancellation rate by restaurant (top 10 worst, minimum 20 orders)
SELECT Restaurant_Name,
       COUNT(*)                                             AS Total_Orders,
       SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END) AS Cancelled_Orders,
       ROUND(100.0 * SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END)
             / COUNT(*), 2)                                 AS Cancellation_Rate_Pct
FROM food_delivery_cleaned
GROUP BY Restaurant_Name
HAVING COUNT(*) >= 20
ORDER BY Cancellation_Rate_Pct DESC
LIMIT 10;

-- D3. Cuisine-wise performance (rating + revenue)
SELECT Cuisine_Type,
       ROUND(AVG(Restaurant_Rating), 2) AS Avg_Rating,
       ROUND(SUM(Final_Amount), 2)      AS Total_Revenue,
       COUNT(*)                         AS Total_Orders
FROM food_delivery_cleaned
GROUP BY Cuisine_Type
ORDER BY Total_Revenue DESC;


-- ---------- E. OPERATIONAL INSIGHTS ----------

-- E1. Peak hour vs non-peak hour demand
SELECT Peak_Hour,
       COUNT(*)                    AS Total_Orders,
       ROUND(AVG(Delivery_Time_Min), 2) AS Avg_Delivery_Time_Min
FROM food_delivery_cleaned
GROUP BY Peak_Hour;

-- E2. Payment mode preferences
SELECT Payment_Mode,
       COUNT(*)                          AS Total_Orders,
       ROUND(100.0 * COUNT(*) /
             (SELECT COUNT(*) FROM food_delivery_cleaned), 2) AS Pct_Of_Orders
FROM food_delivery_cleaned
GROUP BY Payment_Mode
ORDER BY Total_Orders DESC;

-- E3. Cancellation reason breakdown
SELECT Cancellation_Reason,
       COUNT(*) AS Total_Orders
FROM food_delivery_cleaned
WHERE Order_Status = 'Cancelled'
GROUP BY Cancellation_Reason
ORDER BY Total_Orders DESC;


-- ---------- F. TOP-LEVEL KPIs (used on the dashboard) ----------

SELECT
    COUNT(*)                                                        AS Total_Orders,
    ROUND(SUM(Final_Amount), 2)                                     AS Total_Revenue,
    ROUND(AVG(Final_Amount), 2)                                     AS Avg_Order_Value,
    ROUND(AVG(Delivery_Time_Min), 2)                                AS Avg_Delivery_Time_Min,
    ROUND(100.0 * SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                            AS Cancellation_Rate_Pct,
    ROUND(AVG(CASE WHEN Order_Status = 'Delivered' THEN Delivery_Rating END), 2) AS Avg_Delivery_Rating,
    ROUND(AVG(Profit_Margin_Pct), 2)                                AS Avg_Profit_Margin_Pct
FROM food_delivery_cleaned;
