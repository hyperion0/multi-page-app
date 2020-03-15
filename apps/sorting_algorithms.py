from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import numpy as np
from app import app
from utils import Header

appname = "Sorting algorithms"

permutations = []

def selectsort(data_list):
    for i in range(0, len(data_list)):
        min=i
        for j in range(i+1,len(data_list)):
            if(data_list[j]<data_list[min]):
                min=j
        temp=data_list[min]
        data_list[min]=data_list[i]
        data_list[i]=temp

def bubble(list):
    for i in range(len(list) - 1, 0, -1):
        no_swap = True
        for k in range(0, i):
            if list[k + 1] < list[k]:
                list[k], list[k + 1] = list[k + 1], list[k]
                no_swap = False
        if no_swap:
            return

def quicksort(arr, begin, end):

    if end - begin > 1:
        p = partition(arr, begin, end)
        quicksort(arr, begin, p)
        quicksort(arr, p + 1, end)


def partition(arr, begin, end):
    pivot = arr[begin]
    i = begin + 1
    j = end - 1

    while True:
        while i <= j and arr[i] <= pivot:
            i = i + 1
        while i <= j and arr[j] >= pivot:
            j = j - 1

        if i <= j:
            arr[i], arr[j] = arr[j], arr[i]
            permutations.append((i, j))
        else:
            arr[begin], arr[j] = arr[j], arr[begin]
            permutations.append((j, begin))
            return j


n = 100
arr = [i for i in range(n)]
np.random.shuffle(arr)
shuffled_arr_init = arr.copy()
x_range = [i for i in range(n)]

shuffled_arr = arr.copy()


quicksort(arr, 0, len(arr))


def create_frames(shuffled_array, permutations):
    f = []
    for elt in permutations:
        shuffled_array[elt[0]], shuffled_array[elt[1]] = (
            shuffled_array[elt[1]],
            shuffled_array[elt[0]],
        )
        f.append(go.Frame(data=[go.Bar(x=x_range, y=shuffled_array)]))
    return f


initial_data = [go.Bar(x=x_range, y=shuffled_arr_init)]
figure_frames = create_frames(shuffled_arr, permutations)
figquicksort = go.Figure(
    data=initial_data,
    layout=go.Layout(
        title="Quicksort",
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 10, "redraw": False}}],
                    ),
                    dict(
                        label="Replay",
                        method="animate",
                        args=[None, {"frame": {"duration": 10, "redraw": False}}],
                    ),
                ],
            )
        ],
    ),
    frames=figure_frames,
)

layout = html.Div(
    [
        Header(app),
        html.H3(appname),
        html.Div(
            [
                dcc.Graph(figure=figquicksort),
                dcc.Markdown(f"{len(permutations)} permutations"),
            ]
        ),
    ]
)
