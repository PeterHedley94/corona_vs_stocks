# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
from plotly import tools
import datetime
import pandas as pd
import requests
from cov19 import get_cov_data, replace_data
import yfinance as yf

cov_data = get_cov_data()

def normalise_population(row):
    print(row)
    return row

def convert_row(row):
    if row['Population']:
        try:
            row['Population'] = int(row['Population'].replace(",",""))
        except:
            row['Population'] = 1
        return row/row['Population']
    return row

def get_graph(cov_data_full, normalise_pop=False):
    cov_data_full = cov_data.copy()
    
    if normalise_pop:
        cov_data_full = cov_data_full.apply(convert_row, axis=1)
    else:
        cov_data_full = cov_data_full.loc[:,cov_data_full.columns!='Population']

    cov_data_full = cov_data_full.transpose()
    cov_data_full.columns = cov_data.index

    return {
                'data': [
                    {'type':'scatter','mode':'lines', 'showlegend': False,
                    'x': cov_data_full.index,'y': cov_data_full[col],'name': replace_data(col)} for col in cov_data_full.columns
                ],
                'layout': {
                    'title': 'Cov 19 Cases'
                }
            }

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Cov vs Stocks'),
    
    html.Div([
        dcc.Input(id="stock-input", value="SPY", type="text"),
        html.Button(id="submit-button", n_clicks=0, children="Submit")
    ]),
    dcc.Graph(
        id="graph_close",
    )
])

def get_data(input_value):
    df = yf.Ticker(input_value)
    df = df.history(period="2mo")
    df['date'] = pd.to_datetime(df.index)
    df.columns = [i.lower() for i in df.columns]
    return df

@app.callback(Output('graph_close', 'figure'),
              [Input("submit-button", "n_clicks")],
              [State("stock-input", "value")]
              )

def update_fig(n_clicks, input_value):
    df = get_data(input_value)
    trace_line = go.Scatter(x=list(df.date),
                                y=list(df.close),
                                #visible=False,
                                name="Close",
                                showlegend=False)

    trace_candle = go.Candlestick(x=df.date,
                           open=df.open,
                           high=df.high,
                           low=df.low,
                           close=df.close,
                           #increasing=dict(line=dict(color="#00ff00")),
                           #decreasing=dict(line=dict(color="white")),
                           visible=False,
                           showlegend=False)

    trace_bar = go.Ohlc(x=df.date,
                           open=df.open,
                           high=df.high,
                           low=df.low,
                           close=df.close,
                           #increasing=dict(line=dict(color="#888888")),
                           #decreasing=dict(line=dict(color="#888888")),
                           visible=False,
                           showlegend=False)

    data = [trace_line, trace_candle, trace_bar]

    updatemenus = list([
        dict(
            buttons=list([
                dict(
                    args=[{'visible': [True, False, False]}],
                    label='Line',
                    method='update'
                ),
                dict(
                    args=[{'visible': [False, True, False]}],
                    label='Candle',
                    method='update'
                ),
                dict(
                    args=[{'visible': [False, False, True]}],
                    label='Bar',
                    method='update'
                ),
            ]),
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0,
            xanchor='left',
            y=1.05,
            yanchor='top'
        ),
    ])

    cov_graph = get_graph(cov_data)
    
    fig = tools.make_subplots(rows=2, cols=1, shared_xaxes=True)

    for i in data:
        fig.append_trace(i, 2, 1)

    for i in cov_graph['data']:
        fig.append_trace(i, 1, 1)
    

    fig['layout'].update(title='Customizing Subplot Axes',
            updatemenus=updatemenus,
        autosize=False
    )

    # Edit hoveroptions
    fig['layout']['hovermode'] = 'x'

    for ser in range(0,len(fig['data'])):
        fig['data'][ser]['hoverinfo']= 'all'

    return fig


app.css.append_css({
    "external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
    app.run_server(debug=True)