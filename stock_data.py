import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from iexfinance.stocks import Stock
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
import datetime
import pandas as pd
import requests

def update_news():
    url = "https://api.iextrading.com/1.0/stock/market/news/last/5"
    r = requests.get(url)
    print(r)
    json_string = r.json()

    df = pd.DataFrame(json_string)
    df = pd.DataFrame(df[["headline", "url"]])

    return df

def generate_html_table(max_rows=10):

    df = update_news()

    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th()])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.A(
                                        df.iloc[i]["headline"],
                                        href=df.iloc[i]["url"],
                                        target="_blank"
                                    )
                                )
                            ]
                        )
                        for i in range(min(len(df),max_rows))
                    ]
                ),
                style={"height": "300px", "overflowY": "scroll"},
            ),
        ],
        style={"height": "100%"},)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H2("Stock App"),
        html.Img(src="/assets/stock-icon.png")
    ], className="banner"),

    html.Div([
        dcc.Input(id="stock-input", value="SPY", type="text"),
        html.Button(id="submit-button", n_clicks=0, children="Submit")
    ]),

    html.Div([
        html.Div([
            dcc.Graph(
                id="graph_close",
            )
        ], className="six columns"),
    ],className="row")
])

app.css.append_css({
    "external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"
})


@app.callback(Output('graph_close', 'figure'),
              [Input("submit-button", "n_clicks")],
              [State("stock-input", "value")]
              )

def update_fig(n_clicks, input_value):
    from iexfinance.stocks import Stock
    stocks = Stock(input_value,
    token='pk_94a745eade1449549ca177ec47571a90')
    df = pd.DataFrame(stocks.get_historical_prices())

    trace_line = go.Scatter(x=list(df.index),
                                y=list(df.close),
                                #visible=False,
                                name="Close",
                                showlegend=False)

    trace_candle = go.Candlestick(x=df.index,
                           open=df.open,
                           high=df.high,
                           low=df.low,
                           close=df.close,
                           #increasing=dict(line=dict(color="#00ff00")),
                           #decreasing=dict(line=dict(color="white")),
                           visible=False,
                           showlegend=False)

    trace_bar = go.Ohlc(x=df.index,
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

    layout = dict(
        title=input_value,
        updatemenus=updatemenus,
        autosize=False,
        xaxis=list(df.index)
        )

    return {
        "data": data,
        "layout": layout
    }

if __name__=="__main__":
    app.run_server(debug=True, port=5001)