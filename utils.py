import dash_html_components as html
import dash_core_components as dcc

def Header(app):
    return html.Div([get_header(app)])


def get_header(app):
    header = html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src=app.get_asset_url("banner.png"),
                        className="logo",
                        height=195,
                        width=120,
                    ),
                    html.A(
                        html.Button("Index", id="index"),
                        href="/index",
                        className="bannerbutton",
                    ),
                    html.A(
                        html.Button("Sorting Algorithms", id="app1"),
                        href="/apps/sorting_algorithms",
                        className="bannerbutton",
                    ),
                    html.A(
                        html.Button("PathFinding", id="app2"),
                        href="/apps/pathfinding",
                        className="bannerbutton",
                    ),
                    html.A(
                        html.Button("China COVID impact", id="chinacovid"),
                        href="/apps/china_monitoring",
                        className="bannerbutton",
                    ),
                    html.A(
                        html.Button("My LinkedIn", id="linkedin"),
                        href="https://www.linkedin.com/in/axel-bonnet-de-paillerets/",
                        className="bannerbutton",
                    ),
                    html.A(
                        html.Button("Contact me", id="mailme"),
                        href="mailto:axel.depaillerets@gmail.com",
                        className="bannerbutton",
                    ),
                ],
                className="row",
            ),
        ],
        className="row",
    )
    return header


def get_menu():
    menu = html.Div(
        [
            dcc.Link("Index", href="/index", className="tab first",),
            dcc.Link("app1", href="/apps/app1", className="tab",),
            dcc.Link("app2", href="/apps/app2", className="tab",),
            dcc.Link(
                "china_monitoring", href="/apps/china_monitoring", className="tab last",
            ),
        ],
        className="row all-tabs",
    )
    return menu


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table
