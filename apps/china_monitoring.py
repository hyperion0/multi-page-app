# coding: utf-8
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from os import listdir
import requests
from app import app
from utils import Header

appname = "China Monitoring"
filelist = listdir("data")
city_list = [elt.split("-")[0] for elt in filelist]
column_list = [
    " pm25",
    " pm10",
    " o3",
    " no2",
    " so2",
    " co",
]

colors = {"background": "#f9f9f9"}
color_pairs = [
    ["FF0000", "9B0000"],
    ["FF00F7", "9B0096"],
    ["774DFF", "24009B"],
    ["5C9EFF", "0066FF"],
    ["5CFBFF", "059CA1"],
]


def generate_header():
    return html.H2(
        children="Monitoring coronavirus impact on Chinese major cities",
    )


def generate_pollution_container():
    return html.Div(
        [
            html.H3("Pollution in Chinese cities"),
            html.H3("Select pollution particle"),
            dcc.Dropdown(id="column-dropdown", value=[column_list[0]], multi=True),
            html.Div(id="city-pollution-graphs"),
        ],
        className="pretty_container five columns",
    )


def generate_traffic_container():
    return html.Div(
        [html.H3("Traffic in Chinese cities"), dcc.Graph(id="city-traffic-graph"),],
        className="pretty_container five columns",
    )


layout = html.Div(
    children=[ Header(app),
        generate_header(),
        html.Div(
            [
                html.H3("Select a city"),
                dcc.Dropdown(
                    id="city-dropdown",
                    options=[dict(label=city, value=city) for city in city_list],
                    value=city_list[0],
                ),
                html.Div(
                    [
                        html.Div(
                            [   html.H5("Select a pollution particle"),
                                dcc.Dropdown(
                                    id="column-dropdown",
                                    value=[column_list[0]],
                                    multi=True,
                                ),
                                html.Div(
                                    dcc.Graph(id="city-pollution-graph"),
                                    className="graph",
                                ),
                            ],
                            className="six columns",
                        ),
                        html.Div(
                            [   html.H5("Past week traffic congestion compared to historical data"),
                                html.Div(
                                    dcc.Graph(id="city-traffic-graph"),
                                    className="graph",
                                )
                            ],
                            className="six columns",
                        ),
                    ],
                    id="city-graphs",
                    className="row",
                ),
            ],
            className="pretty_container",
        ),
    ],
)


@app.callback(Output("column-dropdown", "options"), [Input("city-dropdown", "value")])
def update_column_dropdown(city):
    return [dict(label=col, value=col) for col in column_list]


@app.callback(
    Output("city-pollution-graph", "figure"),
    [Input("city-dropdown", "value"), Input("column-dropdown", "value")],
)
def update_pollution_figure(selected_city, selected_columns):

    df = pd.read_csv(
        f"data/{selected_city}-air-quality.csv", parse_dates=["date"], na_values=" "
    )
    df = df.sort_values("date")
    df["year"] = df.date.dt.year
    df["dayofyear"] = df.date.dt.dayofyear

    df = df.fillna(method="backfill")

    datalist = []
    for i, selected_column in enumerate(selected_columns):
        df["smoothedts"] = df[selected_column].rolling(14).mean()
        current_year = max(df.year.values)
        df2 = df.set_index(["year", "dayofyear"])["smoothedts"].unstack(level=0)

        past_year_list = df2.iloc[:, :-1].mean(axis=1).tolist()
        current_year_list = df2[current_year].tolist()
        n = max(len(past_year_list), len(current_year_list))
        x = [i for i in range(n)]
        datalist.extend(
            [
                {
                    "x": x,
                    "y": past_year_list,
                    "type": "line",
                    "name": f"Past years average {selected_column}",
                    "marker": {"color": color_pairs[i][0]},
                },
                {
                    "x": x,
                    "y": current_year_list,
                    "type": "line",
                    "name": f"{current_year}  {selected_column}",
                    "marker": {"color": color_pairs[i][1]},
                },
            ]
        )

    figure = {
        "data": datalist,
        "layout": dict(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            # font={"color": colors["text"]},
            margin={"l": 40, "b": 40, "t": 10, "r": 10},
            xaxis={"title": "Day of Year"},
            yaxis={"title": "Air Quality Index"},
        ),
    }
    return figure


@app.callback(
    Output("city-traffic-graph", "figure"), [Input("city-dropdown", "value")],
)
def update_traffic_figure(selected_city):
    url = f"https://api.midway.tomtom.com/ranking/live/CHN%2FCircle%2F{selected_city}"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "fr,en-US;q=0.9,en;q=0.8",
        "if-none-match": 'W/"145c8-9OTwe3gyeRnn4yvE4oV9RmB3LHI"',
        "origin": "https://www.tomtom.com",
        "referer": "https://www.tomtom.com/en_gb/traffic-index/beijing-traffic",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
    }

    with requests.Session() as s:
        r = s.get(url, headers=headers)
    df = pd.DataFrame(r.json()["data"])
    figure = {
        "data": [
            {
                "x": df.index,
                "y": df["TrafficIndexLive"],
                "type": "line",
                "name": "Live Traffic Index",
            },
            {
                "x": df.index,
                "y": df["TrafficIndexHistoric"],
                "type": "line",
                "name": "Historic Traffic Index",
            },
        ],
        "layout": dict(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            # font={"color": colors["text"]},
            margin={"l": 40, "b": 40, "t": 10, "r": 10},
            xaxis={"title": "Past Week"},
            yaxis={"title": "Traffic Index"},
        ),
    }
    return figure

def create_layout(app):
    return layout
