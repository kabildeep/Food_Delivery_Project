import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "food_delivery_db")


CLEANED_FILE = "data/food_delivery_cleaned.csv"
TABLE_NAME = "food_delivery_cleaned"


def upload_data():

    print("Step 1: Reading the cleaned CSV file...")

    df = pd.read_csv(CLEANED_FILE)

    print(
        f"Loaded {df.shape[0]} rows and "
        f"{df.shape[1]} columns."
    )


    print("Step 2: Connecting to MySQL...")


    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME
    )

    engine = create_engine(connection_url)


    print(
        f"Step 3: Uploading data into the "
        f"'{TABLE_NAME}' table..."
    )

    df.to_sql(
        name=TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000
    )


    print("Done! Your cleaned data is now in MySQL.")

    print(
        f" Database: {DB_NAME} | "
        f"Table: {TABLE_NAME}"
    )


if __name__ == "__main__":
    upload_data()

