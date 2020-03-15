from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
from apps import sorting_algorithms, pathfinding, china_monitoring


app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


class index:
    layout = html.Div(
        [
            html.H1("Welcome on my webapp"),
            dcc.Markdown("This is markdown "),
            html.Div(
                [
                    html.A(
                        [
                            html.H3("China Monitoring App", className="indextitle"),
                            html.P("Measure COVID 19 influence on Air quality and traffic in Chinese cities"),
                        ],
                        href="/apps/china_monitoring",
                        className="indexbuttonchina four columns",
                    ),
                    html.A(
                        [html.H3("Sorting Algorithms", className="indextitle")],
                        href="/apps/sorting_algorithms",
                        className="indexbuttonsorting four columns",
                    ),
                    html.A(
                        [html.H3("Pathfinding Algorithm", className="indextitle")],
                        href="/apps/pathfinding",
                        className="indexbutton four columns",
                    ),
                ],
                className="row",
            ),
        ],
        className="column",
    )


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/apps/sorting_algorithms":
        return sorting_algorithms.layout
    elif pathname == "/apps/pathfinding":
        return pathfinding.layout
    elif pathname == "/apps/china_monitoring":
        return china_monitoring.layout
    elif pathname == "/index" or pathname == "/":
        return index.layout
    else:
        return "Error 404   :   Sorry, this URL does not exist :("

server = app.server
if __name__ == "__main__":
    app.run_server(debug=True)