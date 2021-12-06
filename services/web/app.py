import pyspark.sql.functions as F
from pyspark.sql.types import *
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from operator import add
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
import plotly.express as px
app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1("Word Count"),
    dcc.Textarea(
        id='textarea-example',
        value='Textarea content initialized\nwith multiple lines of text',
        style={'width': '100%', 'height': 300},
    ),
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'})
])


@app.callback(
    Output('textarea-example-output', 'children'),
    Input('textarea-example', 'value')
)
def update_output(value):
    try:
        conf = SparkConf().setAppName('letter count')
        sc = SparkContext(conf=conf)
    except Exception as e:
        print(e)
    sc.stop()
    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .getOrCreate()
    df = spark.read \
        .format("csv") \
        .option("header", True) \
        .load("./data.csv")
    magic_percentile = F.expr('percentile_approx(purchase_price, 0.5)')
    data = df.groupby('suburb').agg(magic_percentile.alias('med_val')).collect()
    
    return 'Number of Words: \n{}'.format(data)




if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")


