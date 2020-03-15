from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
import dash_canvas
from dash_canvas import DashCanvas
from app import app
from utils import Header
import numpy as np
from skimage import io, color, img_as_ubyte
import os
import json
from skimage import draw, morphology
from scipy.ndimage import binary_dilation
import logging
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from io import BytesIO
import base64


def array_to_data_url(img, dtype=None):
    """
    Converts numpy array to data string, using Pillow.

    The returned image string has the right format for the ``image_content``
    property of DashCanvas.

    Parameters
    ==========

    img : numpy array

    Returns
    =======

    image_string: str
    """
    if dtype is not None:
        img = img.astype(dtype)
    pil_img = Image.fromarray(img)
    buff = BytesIO()
    pil_img.save(buff, format="png")
    prefix = b'data:image/png;base64,'
    image_string = (prefix + base64.b64encode(buff.getvalue())).decode("utf-8")
    return image_string

logger = logging.getLogger()
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.DEBUG)

# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def _indices_of_path(path, scale=1):
    """
    Retrieve pixel indices (integer values). 

    Parameters
    ----------

    path: SVG-like path formatted as JSON string
        The path is formatted like
        ['M', x0, y0],
        ['Q', xc1, yc1, xe1, ye1],
        ['Q', xc2, yc2, xe2, ye2],
        ...
        ['L', xn, yn]
        where (xc, yc) are for control points and (xe, ye) for end points.

    Notes
    -----

    I took a weight of 1 and it seems fine from visual inspection.
    """
    rr, cc = [], []
    for (Q1, Q2) in zip(path[:-2], path[1:-1]):
        # int(round()) is for Python 2 compatibility
        inds = draw.bezier_curve(
            int(round(Q1[-1] / scale)),
            int(round(Q1[-2] / scale)),
            int(round(Q2[2] / scale)),
            int(round(Q2[1] / scale)),
            int(round(Q2[4] / scale)),
            int(round(Q2[3] / scale)),
            1,
        )
        rr += list(inds[0])
        cc += list(inds[1])
    return rr, cc


def filter_inds(inds, shape):
    """Filter inds couples where one of the indice is going out of shape size

    Parameters
    ----------

    inds : tuple
        tuple contains X and Y two lists of int, coordinates
    shape : tuple 
        (int, int), shape of underlying image

    Returns
    -------
    filter_inds : tuple
        filtered x and y couples smaller than 
    """
    x_f = []
    y_f = []
    for x, y in zip(inds[0], inds[1]):
        if x < shape[0] and y < shape[1]:
            x_f.append(x)
            y_f.append(y)
    filter_inds = (x_f, y_f)
    return filter_inds


def parse_jsonstring(string, shape=None, scale=1):
    """
    Parse JSON string to draw the path saved by react-sketch.

    Up to now only path objects are processed (created with Pencil tool).

    Parameters
    ----------

    data : str
        JSON string of data
    shape: tuple, optional
        shape of returned image.

    Returns
    -------

    mask: ndarray of bools
        binary array where the painted regions are one.
    """
    if shape is None:
        shape = (500, 500)
    mask = np.zeros(shape, dtype=np.bool)
    try:
        data = json.loads(string)
    except:
        return mask
    scale = 1
    for obj in data["objects"]:
        if obj["type"] == "image":
            scale = obj["scaleX"]
        elif obj["type"] == "path":
            scale_obj = obj["scaleX"]
            inds = _indices_of_path(obj["path"], scale=scale / scale_obj)
            radius = round(obj["strokeWidth"] / 2.0 / scale)
            mask_tmp = np.zeros(shape, dtype=np.bool)
            inds = filter_inds(inds, shape)
            mask_tmp[inds[0], inds[1]] = 1
            mask_tmp = binary_dilation(mask_tmp, morphology.disk(radius))
            mask += mask_tmp
    return mask


appname = "Pathfinding"


filename = "https://raw.githubusercontent.com/hyperion0/multi-page-app/master/assets/pathfinding.png"
img = io.imread(filename, as_gray=True)
height, width = img.shape
img_str = io.imread(filename)
logging.info(f"img shape {img.shape}")
layout = html.Div(
    [
        Header(app),
        html.H3(appname),
        DashCanvas(
            id="canvas",
            filename=filename,
            hide_buttons=["line", "zoom", "pan"],
            goButtonTitle="Find Path",
        ),
        dcc.Markdown(img.shape, id="log"),
        dcc.Graph(id="pathgraph", figure={"data": [go.Heatmap()]}),
    ]
)


@app.callback(
    [Output("pathgraph", "figure"), Output("canvas", "image_content")],
    [Input("canvas", "json_data")],
)
def update_data(string):
    if string:
        mask = parse_jsonstring(string, img.shape)
    else:
        raise PreventUpdate

    data = (255 * mask).astype(np.uint8)
    data_str = array_to_data_url(data)

    data = [data[i, :] for i in range(data.shape[0])]

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=data,
                colorscale=[[0, "white"], [0.5, "white"], [0.5, "black"], [1, "black"]],
            )
        ]
    )
    return fig, data_str
