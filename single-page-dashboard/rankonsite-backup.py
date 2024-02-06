import dash
from dash import dash_table as dt
from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output,State
import plotly.graph_objs as graph_objs
import pandas as pd 
import plotly.express as px
import psycopg2
from sqlalchemy import create_engine
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
#connecting to database 
def connect_to_db():
  conn = psycopg2.connect(
            host = '10.62.48.125',
            dbname = 'bdc_extranet_data',
            user = 'readonly_user',
            password = 'readonlypassword',
            port = 5432 
            )
  return conn

def load_data():
    conn = connect_to_db()
    #creating dataframes with tables
    bdc_us_active_property_list = 'select * from bdc_us_active_property_list'  # Replace with your query
    data_us_prop_list = pd.read_sql_query(bdc_us_active_property_list, conn)

    bdc_us_opportunity_data = 'SELECT * FROM bdc_us_opportunity_data'
    data_us_opp_data = pd.read_sql_query(bdc_us_opportunity_data, conn)

    bdc_comp_properties = 'SELECT * FROM bdc_comp_properties'
    data_comp_prop = pd.read_sql_query(bdc_comp_properties, conn)

    bdc_us_rankonsite_data = 'SELECT * FROM bdc_us_rankonsite_data'
    data_rankonsite_oyo = pd.read_sql_query(bdc_us_rankonsite_data, conn)

    bdc_compset_sales_insights_data = 'SELECT * FROM bdc_compset_sales_insights_data'
    data_compset_sales = pd.read_sql_query(bdc_compset_sales_insights_data, conn)

    bdc_us_reviewonsite_data = 'SELECT * FROM bdc_us_reviewonsite_data'
    data_reviewonsite_data = pd.read_sql_query(bdc_us_reviewonsite_data, conn)
  
    conn.close()
    return data_us_prop_list,data_us_opp_data, data_comp_prop,data_rankonsite_oyo,data_compset_sales,data_reviewonsite_data
 
data_us_prop_list,data_us_opp_data, data_comp_prop,data_rankonsite_oyo,data_compset_sales,data_reviewonsite_data = load_data()
#print(data_rankonsite_oyo)
data_rankonsite_oyo.dtypes


app = dash.Dash(__name__)

# Define layout using Dash components
app.layout = html.Div([
    html.H1(children="Competitor Dashboard",
            style={"fontSize": "48px", "color": "red", "text-align": "center", 'width': '100%', 'margin-bottom': '20px'},
            ),

    html.Div([
        html.Div("Oyo ID:", style={'width': '30%', 'display': 'inline-block', 'font-weight': 'bold'}),
        dcc.Dropdown(
            id='oyo-id-dropdown',
            options=[
                {'label': oyo_id, 'value': oyo_id} for oyo_id in data_rankonsite_oyo['oyo_id'].unique()
            ],
            value=data_rankonsite_oyo['oyo_id'].iloc[0],  # Set default value
            multi=True,
            searchable=False,
            placeholder="Select oyo_id",
            style={'width': '60%'},
        ),
    ], style={'margin-right': '5px', 'display': 'flex', 'margin-bottom': '20px'}),

    html.Div([
        html.Label('Select comp Distance Range (miles):'),
        dcc.RangeSlider(
            id='distance-slider',
            marks={i: str(i) for i in range(0, 31, 5)},  # Marks every 5 miles
            min=0,
            max=30,
            step=3,
            value=[0, 30]  # Initial range
        ),
    ], style={'margin-top': '20px', 'margin-bottom': '20px'}),

    # Start Date Section
    html.Div([
        html.Label(html.Div("Start Date ", style={'width': '30%', 'font-weight': 'bold', 'display': 'inline-block'})),
        dcc.DatePickerSingle(
            id="start-date",
            date=data_rankonsite_oyo['date'].min(),
        ),
    ], style={'margin-right': '5px', 'margin-bottom': '20px'}),

    # End Date Section
    html.Div([
        html.Label(html.Div("End Date ", style={'width': '30%', 'font-weight': 'bold', 'display': 'inline-block'})),
        dcc.DatePickerSingle(
            id="end-date",
            date=data_rankonsite_oyo['date'].max(),
        ),
    ], style={'margin-right': '10px', 'margin-bottom': '20px'}),

    html.Button('Submit', id='submit-button', n_clicks=0,
                style={'margin-left': '50%', 'width': '30%', 'fontSize': 18, 'color': 'white', 'font-weight': 'bold',
                       'background-color': 'green', 'margin-bottom': '20px'}),

    # Tabs
    dcc.Tabs(id='tabs', value='Opportunity_data', children=[
        dcc.Tab(label='Rank & Review on site', value='Rank & Review on site',
                style={'fontSize': 18, 'color': 'white', 'font-weight': 'bold', 'background-color': 'red'}),
    ]),

    html.Div(id='tabs-content'),

])


# Callback to update the plots based on the selected Oyo ID, start date, and end date
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('submit-button', 'n_clicks')],
    [State('oyo-id-dropdown', 'value'),
     State('start-date', 'date'),
     State('end-date', 'date'),
     State('distance-slider', 'value')]
)
def update_tab_content(selected_tab, n_clicks, selected_oyo_ids, start_date, end_date, distance_slider_value):
    if n_clicks > 0:
        filtered_data = data_rankonsite_oyo[
            (data_rankonsite_oyo['oyo_id'].isin(selected_oyo_ids)) &
            (data_rankonsite_oyo['date'] >= start_date) &
            (data_rankonsite_oyo['date'] <= end_date)
        ]

        if selected_tab == 'Rank & Review on site':
            bar_chart_1 = create_bar_chart_1(filtered_data, selected_oyo_ids)
            bar_chart_2 = create_bar_chart_2(filtered_data, selected_oyo_ids)
            bar_chart_3 = create_bar_chart_3(filtered_data, selected_oyo_ids)
            return [
                html.Div([
                    html.H3('Content of Rank & Review on site',
                            style={"fontSize": "30px", "color": "green", "text-align": "center", 'width': '100%',
                                   'margin-bottom': '20px'}),
                    dcc.Graph(figure=bar_chart_1),
                    dcc.Graph(figure=bar_chart_2),
                    dcc.Graph(figure=bar_chart_3),
                ])
            ]
    else:
        return [html.Div([])]

def create_bar_chart_1(data, selected_oyo_ids):
    # Implement logic to create grouped bar chart based on the filtered data
    fig = px.bar(data, x='date', y='impressions', color='oyo_id',
                 labels={'impressions': 'Impressions'},
                 title=f'Impressions for Oyo IDs: {", ".join(selected_oyo_ids)}')
    return fig

def create_bar_chart_2(data, selected_oyo_ids):
    # Implement logic to create grouped bar chart based on the filtered data
    fig = px.bar(data, x='date', y='pageviews', color='oyo_id',
                 labels={'pageviews': 'pageviews'},
                 title=f'pageviews for Oyo IDs: {", ".join(selected_oyo_ids)}')
    return fig

def create_bar_chart_3(data, selected_oyo_ids):
    # Implement logic to create grouped bar chart based on the filtered data
    fig = px.bar(data, x='date', y='bookings', color='oyo_id',
                 labels={'bookings': 'bookings'},
                 title=f'Bookings for Oyo IDs: {", ".join(selected_oyo_ids)}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
