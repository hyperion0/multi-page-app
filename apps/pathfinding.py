from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
import dash_canvas
from dash_canvas import DashCanvas
from app import app
from utils import Header
from dash_canvas.utils import array_to_data_url, parse_jsonstring
import numpy as np
from skimage import io, color, img_as_ubyte
import os




appname = "Pathfinding"

filename = "assets/mitochondria.jpg"
img = io.imread(filename, as_gray=True)
height, width = img.shape
img_str= io.imread(filename)

layout = html.Div(
    [
        Header(app),
        html.H3(appname),
        DashCanvas(
            id="canvas",
            filename=filename,
            #image_content= img_str,
            # hide_buttons=["line", "zoom", "pan"],
            goButtonTitle="Find Path",
        ),
        html.Div([html.Img(id="my-image", width=500)]),
        dcc.Markdown(img.shape)
    ]
)


import dash
import dash_html_components as html
from dash_canvas import DashCanvas
import numpy as np



canvas_width = 500


layout = html.Div([
    DashCanvas(id='canvas_image',
               tool='line',
               lineWidth=5,
               lineColor='red',
               filename=filename,
               width=canvas_width)
    ])

@app.callback(Output("my-image", "src"), [Input("canvas", "json_data")])
def update_data(string):
    if string:
        mask = parse_jsonstring(string, img.shape)
    else:
        raise PreventUpdate
    return array_to_data_url((255 * mask).astype(np.uint8))
