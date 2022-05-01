"""Imports for the main.py file"""
import threading
from datetime import date
from typing import List

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pyspark.sql.functions as SparkFunctions

# import pyspark.sql.functions as F
# import pyspark.sql.types as SparkTypes
from dash import dcc
from dash.dependencies import Input, Output
from pyspark.sql import SparkSession
from services.web.api.pg_csv import load_data

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        dbc.Button("Update", id="update_btn", n_clicks=0, color="primary"),
        dcc.DatePickerSingle(
            id="startdate",
            min_date_allowed=date(1990, 8, 5),
            initial_visible_month=date(2019, 8, 5),
            date=date(2019, 8, 5),
        ),
        dcc.DatePickerSingle(
            id="enddate",
            min_date_allowed=date(1995, 8, 5),
            initial_visible_month=date(2020, 8, 5),
            date=date(2020, 8, 5),
        ),
        dcc.Dropdown(
            id="suburb",
            options=[
                {"label": "Sydney", "value": "SYDNEY"},
                {"label": "ZETLAND", "value": "ZETLAND"},
                {"label": "YOUNG", "value": "YOUNG"},
            ],
            value="SYDNEY",
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div(id="hidden", style={"display": "none"}),
        dcc.Loading(
            id="ls-loading-1", children=[html.Div(id="content")], type="default"
        ),
    ]
)


@app.callback(Output("hidden", "children"), Input("update_btn", "n_clicks"))
def background_data_retriving(n_clicks: int) -> None:
    """Data retriving function"""
    if n_clicks == 0:
        return
    threading.Thread(target=load_data)

    return


@app.callback(
    Output("content", "children"),
    [Input("startdate", "date"), Input("enddate", "date"), Input("suburb", "value")],
)
def update_output(startdate, enddate, suburb) -> List:
    """
    Callback functions
    """
    if startdate > enddate:
        return ["Invalid Start Date!"]

    spark = SparkSession.builder.appName("Python Spark SQL basic example").getOrCreate()
    spark_data_frame = (
        spark.read.format("csv").option("header", True).load("./data.csv")
    )
    spark_data_frame = spark_data_frame.filter(
        spark_data_frame["contract_date"].between(startdate, enddate)
    ).filter(spark_data_frame["suburb"] == suburb)

    spark_data_frame = spark_data_frame.withColumn(
        "df_year", SparkFunctions.year(spark_data_frame["contract_date"])
    )
    spark_data_frame = spark_data_frame.withColumn(
        "df_month", SparkFunctions.month(spark_data_frame["contract_date"])
    )
    spark_data_frame = spark_data_frame.withColumn(
        "df_quarter", SparkFunctions.quarter(spark_data_frame["contract_date"])
    )
    spark_data_frame = spark_data_frame.withColumn(
        "df_weekly", SparkFunctions.weekofyear(spark_data_frame["contract_date"])
    )
    magic_percentile = SparkFunctions.expr("percentile_approx(purchase_price, 0.5)")

    data_yearly = spark_data_frame.groupby(["suburb", "df_year"]).agg(
        magic_percentile.alias("med_val")
    )
    data_monthly = (
        spark_data_frame.groupby(["suburb", "df_year", "df_month"])
        .agg(magic_percentile.alias("med_val"))
        .orderBy("df_year", ascending=False)
    )
    data_quarterly = spark_data_frame.groupby(["suburb", "df_year", "df_quarter"]).agg(
        magic_percentile.alias("med_val")
    )
    data_weekly = spark_data_frame.groupby(["suburb", "df_year", "df_weekly"]).agg(
        magic_percentile.alias("med_val")
    )

    df_monthyear = data_monthly.toPandas()
    df_monthyear["period"] = (
        df_monthyear["df_month"].astype(str) + "-" + df_monthyear["df_year"].astype(str)
    )
    df_quarteryear = data_quarterly.toPandas()
    df_quarteryear["period"] = (
        df_quarteryear["df_quarter"].astype(str)
        + "-"
        + df_quarteryear["df_year"].astype(str)
    )

    df_weeklyyear = data_weekly.toPandas()
    df_weeklyyear["period"] = (
        df_weeklyyear["df_weekly"].astype(str)
        + "-"
        + df_weeklyyear["df_year"].astype(str)
    )
    df_year = data_yearly.toPandas()
    df_year["period"] = df_year["df_year"].astype(str)
    fig = px.line(
        df_year.sort_values(by="df_year"),
        x="period",
        y="med_val",
        title=f"Median value of {suburb} in Yearly",
        markers=True,
    )

    fig1 = px.line(
        df_monthyear.sort_values(by=["df_month", "df_year"], ascending=True),
        x="period",
        y="med_val",
        title=f"Median value of {suburb} in Monthly",
        markers=True,
    )

    fig2 = px.line(
        df_quarteryear.sort_values(by=["df_year"], ascending=True),
        x="period",
        y="med_val",
        title=f"Median value of {suburb} in Quarterly",
        markers=True,
    )
    fig3 = px.line(
        df_weeklyyear.sort_values(by=["df_year"], ascending=True),
        x="period",
        y="med_val",
        title=f"Median value of {suburb} in Weekly",
        markers=True,
    )
    return [
        dcc.Graph(figure=fig),
        dcc.Graph(figure=fig1),
        dcc.Graph(figure=fig2),
        dcc.Graph(figure=fig3),
    ]


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="8000")
