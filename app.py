import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt

from dash_html_components.P import P
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

from model import prediction


app = dash.Dash(__name__)
server = app.server
app.title="Stocks Dash"

#two divisions
app.layout = html.Div([
    html.Div(
        [   html.Img(src="https://www.teahub.io/photos/full/298-2987846_stock-market-wall.jpg", className='Image'),
            html.P("Welcome to the Stock Dash App!", className="start"),

            html.Div([
                #stock input code
                html.P('Input stock code:'),
                dcc.Input(id="code",type="text",placeholder="Stock Code",className="box"),
                html.Button('Submit', id='Submit',className='button')
            ]),

            html.Div([html.Div("Select Date Range: "),
                # Date range picker input
                dcc.DatePickerRange(
                    id="date-picker-single",
                    min_date_allowed=dt(1985, 8, 5),
                    max_date_allowed=dt.now(),
                    initial_visible_month=dt.now(),
                    end_date=dt.now().date()),
            ]),
            html.Div([
                # Stock price button
                html.Button('Stock price', id='Stock price',className='button'),
                # Indicators button
                html.Button('Indicators', id='Indicators',className='button'),
                # Number of days of forecast input
                html.Div("Enter number of Days: "),
                dcc.Input(placeholder='Number of days',type='text',id='days',className="box"),
                # Forecast button
                html.Button('Forecast', id='Forecast',className='button')
            ])
            
        ],className="nav"), 

    html.Div(
        [
            html.Div(
            [   # Logo
                html.Img(id="logo"),
                # Company Name
                html.P(id="company_name", className="start"),    
            ],            className="header"),
            #Description
            html.Div(id="description", className="decription_ticker"),
            # Stock price plot
            html.Div([], id="graphs-content"),
            # Indicator plot
            html.Div([], id="main-content"),
            # Forecast plot
            html.Div([], id="forecast-content")
        ],className="content")

],className="container")

# callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"), 
    Output("company_name", "children"),
    Output("Stock price", "n_clicks"),
    Output("Indicators", "n_clicks"),
    Output("Forecast", "n_clicks")],
    [Input("Submit", "n_clicks")],[State("code", "value")])
def update_data(n, val):  # input parameter(s)
        if val == None:
            raise PreventUpdate
        else:
            company_name= yf.Ticker(val)
            inf = company_name.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url','longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[0], df['shortName'].values[0], None, None, None 

# callback for stock graphs
@app.callback([
    Output("graphs-content", "children"),
], [
    Input("Stock price", "n_clicks"),
    Input('date-picker-single', 'start_date'),
    Input('date-picker-single', 'end_date')
], [State("code", "value")])
def stock_price(n,start_date, end_date, val):
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]

def get_stock_price_fig(df):
    fig = px.line(df,
                x= 'Date',
                y= ["Close", "Open"],
                title="Closing and Opening Price vs Date")

    return fig

# callback for indicators
@app.callback([
    Output("main-content", "children"),
], [
    Input("Indicators", "n_clicks"),
    Input('date-picker-single', 'start_date'),
    Input('date-picker-single', 'end_date')
], [State("code", "value")])
def indicators(n,start_date, end_date, val):
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_more(df)
    return [dcc.Graph(figure=fig)]

def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
    x= 'Date',
    y= "EWA_20",
    title="Exponential Moving Average vs Date")
    fig.update_traces(mode= 'lines+markers')
    return fig

# call back for forecast
@app.callback([Output("forecast-content", "children")],
    [Input("Forecast", "n_clicks")],
    [State("days", 'value'), 
    State("code", "value")])
def forecast(n, days, val):
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)