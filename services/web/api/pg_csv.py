"""Importing libraries"""
import logging

import pandas as pd
from dotenv import load_dotenv
from pony.orm import Database, db_session
from sqlalchemy import create_engine

logging.basicConfig()
log = logging.getLogger("myapp")

load_dotenv()


def load_data() -> None:
    """
    Loading Data from Postgres db.
    """
    log.info("Starting loading data from azure to local postgres!")
    db1 = Database()
    db1.bind(
        provider="postgres",
        user="pgadmin@pg-gp-leadingdata-dev",
        password="Server2020",
        host="pg-gp-leadingdata-dev.postgres.database.azure.com",
        database="NSWSales",
    )
    with db_session:
        records = db1.select(
            """SELECT propertylocality as suburb,
                propertypostcode as postcode,
                CAST(purchaseprice as INTEGER) as purchase_price,
                TO_DATE(contractdate,'yyyymmdd') as contract_date,
                CASE
                WHEN stratalotnumber = '' THEN '1' END as house_num, CASE
                WHEN stratalotnumber!='' THEN stratalotnumber END as unit_num \
                FROM salesrecords_b WHERE NOT contractdate='' AND NOT purchaseprice='';"""
        )
    column_names = [
        "suburb",
        "postcode",
        "purchase_price",
        "contract_date",
        "house_num",
        "unit_num",
    ]
    sales_records = pd.DataFrame(records)
    sales_records.columns = column_names
    engine = create_engine("postgresql://postgres:password@db:5432/postgres")
    sales_records.to_sql("salesrecords_b", engine, if_exists="replace")
    log.info("Loading data from azure to local postgres Completed!")
    log.info("Calling load_pg_to_csv function for latest update")
    load_pg_to_csv()


def load_pg_to_csv() -> None:
    """
    Loading data from postgress server to csv files
    """
    log.info("Starting converting local postgres data to csv file!")
    db1 = Database()
    db1.bind(
        provider="postgres",
        user="postgres",
        password="password",
        host="db",
        database="postgres",
    )
    with db_session:
        records = db1.select(
            """SELECT suburb,postcode,purchase_price,contract_date,
                unit_num,house_num FROM salesrecords_b UNION \
                SELECT suburb_name as suburb,postcode  as postcode,
                CAST(purchase_price as numeric) as purchase_price,
                TO_DATE(contract_date,'dd/mm/yyyy') as contract_date,
                CASE WHEN unit_num='' THEN null END unit_num,
                CASE WHEN house_num='' THEN null END house_num
                FROM legacysalesrecords_b"""
        )
        column_names = [
            "suburb",
            "postcode",
            "purchase_price",
            "contract_date",
            "house_num",
            "unit_num",
        ]
    sales_data_frame = pd.DataFrame(records)
    sales_data_frame.columns = column_names
    sales_data_frame.to_csv("data.csv")
    log.info("Converting local postgres data to csv file Done!")
