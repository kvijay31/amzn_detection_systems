# app.py
import dash
import dash_bootstrap_components as dbc
import base64
import datetime
import io
import pandas as pd
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
import json
import requests
from uuid import uuid4
from parse_contents import pre_process



external_stylesheets = [dbc.themes.SUPERHERO]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

application = app.server
app.config.suppress_callback_exceptions = True

import dash
import dash_html_components as html
import dash_core_components as dcc



# layout = html.Div([
#     html.H1('Review Detector', style={'text-align': 'center', 'margin-top': '30px'}),
#     html.Label('Enter some text:', style={'font-weight': 'bold', 'margin-top': '30px'}),
#     dcc.Input(
#         id='input-text',
#         type='text',
#         placeholder='Enter review here',
#         style={'margin': '10px 0', 'width': '80%'}
#     ),
#     dcc.Dropdown(
#         id='dropdown',
#         options=[
#             {'label': 'Rating Management Explicit', 'value': 'Rating Management Explicit'},
#             {'label': 'Disagreement With Rating', 'value': 'Disagreement With Rating'},
#             {'label': 'Zero Star', 'value': 'Zero Star'},
#             {'label': 'Wrong Buying', 'value': 'Wrong Buying'}
#         ],
#         placeholder='Select Classifier',
#         style={'margin': '10px 0', 'color': 'black'}
#     ),
#     html.Button('Submit', id='submit-button', n_clicks=0, style={'margin': '30px 0'}),
#     html.Div(id='output', style={'margin-top': '50px'})
# ], style={'width': '80%', 'margin': '0 auto'})
import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    html.H1('Review Detector', style={'text-align': 'center', 'margin-top': '30px'}),
    html.Label('Enter some text:', style={'font-weight': 'bold', 'margin-top': '30px'}),
    dcc.Input(
        id='input-text',
        type='text',
        placeholder='Enter review here',
        style={'margin': '10px 0', 'width': '80%'}
    ),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Rating Management Explicit', 'value': 'Rating Management Explicit'},
            {'label': 'Disagreement With Rating', 'value': 'Disagreement With Rating'},
            {'label': 'Zero Star', 'value': 'Zero Star'},
            {'label': 'Wrong Buying', 'value': 'Wrong Buying'},
            {'label': 'Wish I had Read Reviews', 'value': 'Wish I had Read Reviews'}
        ],
        placeholder='Select Classifier',
        style={'margin': '10px 0', 'color': 'black'}
    ),
    html.Button('Submit', id='submit-button', n_clicks=0, style={'margin': '30px 0'}),
    dcc.Loading(
        id='loading',
        children=[html.Div(id='output')],
        type='circle', 
        fullscreen=False, 
        className='custom-loading-style'
    )
], style={'width': '80%', 'margin': '0 auto'})





@app.callback(
    dash.dependencies.Output('output', 'children'),
    dash.dependencies.Input('submit-button', 'n_clicks'),
    dash.dependencies.State('input-text', 'value'),
    dash.dependencies.State('dropdown', 'value')
)
def update_output(n_clicks, input_text, dropdown_value):
    if n_clicks > 0:
        # now, we take the input text, dropdown value and make prediction for the specific classifier: 
        test = type(input_text)
        # return f'The input text is "{test}" and the selected option is "{dropdown_value}".'
        return pre_process(input_text, dropdown_value)
    

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return layout
    else:
        return html.Div([])


if __name__ == '__main__':
    application.run( debug=True, port =  8081)
