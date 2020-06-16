# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


# specify path of data file - should be in same directory as app.py
# use this to run app on local host
#DATAPATH = '/Users/emuckley/Documents/GitHub/hosted_dashboard/STARRYDB_interpolated_pp_wc.csv'
# use this to run app on remote server
DATAPATH = 'STARRYDB_interpolated_pp_wc.csv'

# title for the browser page tab
TITLE = 'STARRYDB explorer'


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def format_var(v):
    """Format a string variable to remove the 'XXX: ' prefix if it exists"""
    if v is None:
        return 'None'
    if isinstance(v, str):
        return v.split(': ')[1] if ': ' in v else v


def get_filtering_options(df):
    """Get dropdown options to show for filtering variables"""
    options = []
    # get list of all column names that aren't ints or floats
    c_raw_list = list(
        df.dtypes[df.dtypes != 'int64'][df.dtypes != 'float64'].index)
    for c_raw in c_raw_list:
        c = format_var(c_raw)
        options.append({'label': c, 'value': c_raw})
    return options


def get_plotting_options(df):
    """Get the dropdown options to show for plotting variables"""
    options = []
    for c_raw in list(df):
        c = format_var(c_raw)
        options.append({'label': c, 'value': c_raw})
    return options


def get_labels(col):
    """Get labels to use as hover text over points, based on the
    name of the column thats being plotted"""
    return list(df['FORMULA'].iloc[np.where(df[col].notnull())[0]])

  
def get_plot_layout(title='Title', xlabel='X-label', ylabel='Y-label'):
    """Create the layout dictionary that gets passed to the plot"""
    layout = {
        'title': title,
        'xaxis': {'title': xlabel},
        'yaxis': {'title': ylabel},
        #'width': 1000,
        #'height': 600,
        'margin': {'l': 150, 'r': 150, 'b': 150, 't': 50}}
    return layout
     
    

# import data into dataframe
df = pd.read_csv(DATAPATH)[::50]
# use this for fast testing
#df = pd.DataFrame(np.random.random((30, 4)), columns=['a','b','c','d'])

# get the options to show in the dropdown menus
plotting_options = get_plotting_options(df)
filtering_options = get_filtering_options(df)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#import flask
#server = flask.Flask(__name__)
#server.secret_key = os.environ.get(
#    'secret_key', str(np.random.randint(0, 1000000)))


import dash
import dash_core_components as dcc
import dash_html_components as html


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# setup the server and app
app = dash.Dash(__name__)
app.title = TITLE
server = app.server  # this line is required for web hosting


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Put your Dash page layout code here

# create app layout
app.layout = html.Div(children=[
    
    # top heading
    html.H1(children=TITLE),

    # create HTML division with paragraph for intro information
    html.Div([
        html.P([
            html.B('Dataset: '), str(DATAPATH), html.Br(),
            html.B('Total rows: '), str(df.shape[0]), html.Br(),
            html.B('Total columns: '), str(df.shape[1]), html.Br(),
            ])]),

    html.Br(),


    html.Div([html.P([
        html.B('Select a variable to plot on the X-axis.')
        ])]),


    # division for the X dropdown menu
    html.Div([
        dcc.Dropdown(
            id='x_var_dropdown',
            clearable=False,
            options=plotting_options,
            value=plotting_options[1]['value'],
            placeholder="Select variable for X-axis (optional)",
            style=dict(width='50%', verticalAlign="middle"))]),
    
    
    
    html.Div([html.P([
        html.B('Select a variable to plot on the Y-axis.'),
        ])]),
    
    

    # division for the Y dropdown menu
    html.Div([
        dcc.Dropdown(
            id='y_var_dropdown',
            clearable=False,
            options=plotting_options,
            value=plotting_options[2]['value'],
            placeholder="Select variable for Y-axis",
            style=dict(width='50%', verticalAlign="middle"))]),
    
 
    
    html.Div([html.P([
        html.B('Select a variable which filters the results.'),
               ])]),
    
    # division for the filtering dropdown menu
    html.Div([
        dcc.Dropdown(
            id='filter_var_dropdown',
            options=filtering_options,
            placeholder="Select variable for filtering (optional)",
            style=dict(width='50%', verticalAlign="middle"))]),   
    
    
    html.Div([html.P([
            'To hide a filter category from the plot, click its entry in the plot legend.',
            html.Br(),
            'To show only one filter category in the plot, double-click that category in the plot legend.'
            ])]),

    html.Br(),

    # create plot
    dcc.Graph(id='graph', config={"displaylogo": False}),


])

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Here, create callbacks which are used by objects on the page

# update graph
@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('x_var_dropdown', 'value'),
     dash.dependencies.Input('y_var_dropdown', 'value'),
     dash.dependencies.Input('filter_var_dropdown', 'value')])
def update_graph(X, Y, F):
    """Update the graph when variable selections are changed"""
    
    dfs = df[[X, Y]].dropna()
    x = list(dfs[X])
    y = list(dfs[Y])
    record_num = len(y)  
    hover_text = get_labels(Y)


    # if we're not filtering the data, plot all of it
    if F is None:
        data_list = [
                {'x': x, 'y': y,
                 'text': hover_text,
                 'hoverinfo': 'text',
                 'mode': 'markers',
                 'marker': {'size': 6}}
                ]
        filter_categories = []



    # if we're filtering the data, split it into different groups
    else:
        # get filter categories
        filter_categories = list(np.unique(df[F].astype(str)))
        
    
        # create list of data dictionaries to be plotted. each dict has form:
        #{'x': x, 'y': y, 'mode': 'markers', 'marker': {'size': 6}, **kwargs}
        data_list = []
        for i in range(len(filter_categories)):
            data_list.append({
                'x': [], 'y': [], 'text': [],
                'name': filter_categories[i],
                'hoverinfo': 'text',
                'mode': 'markers',
                'marker': {'size': 6}})


        # now populate the data list with data
        # loop over each record and add it to the data
        for i in range(len(df)):
            
            # loop over each dtaset in the data list
            for ds in data_list:
                if df[F].iloc[i] == ds['name']:
                    ds['x'].append(df[X].iloc[i])
                    ds['y'].append(df[Y].iloc[i])
                    ds['text'].append(df['FORMULA'].iloc[i])


    # create plot layout
    layout = get_plot_layout(
            title='Showing {} records filtered by {} categories'.format(
                record_num, len(filter_categories)),
            xlabel=format_var(X),
            ylabel=format_var(Y))


    return {'data': data_list, 'layout': layout}
            








'''
# update division which reads dropdown menu
@app.callback(
    dash.dependencies.Output('x_var_display', 'children'),
    [dash.dependencies.Input('x_var_dropdown', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)
'''

             
if __name__ == '__main__':
    app.run_server(debug=True)
