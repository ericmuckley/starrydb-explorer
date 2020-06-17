# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


# specify path of data file - should be in same directory as app.py
# use this to run app on local host
#DATAPATH = '/Users/emuckley/Documents/GitHub/hosted_dashboard/STARRYDB_interpolated_pp_wc.csv'
# use this to run app on remote server
DATAPATH = 'STARRYDB_interpolated_pp_wc.csv'

# title for the browser page tab
TITLE = 'StarryDB explorer'


# import data into dataframe
df = pd.read_csv(DATAPATH)#[::10]
#df.fillna('N/A', inplace=True)
df.replace(False, 'False', inplace=True)
df.replace(True, 'True', inplace=True)

# use this for fast testing
#df = pd.DataFrame(np.random.random((30, 4)), columns=['a','b','c','d'])


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
    return [{'label': c, 'value': c} for c in list(df)]


def get_point_size_options(df):
    """Get options for to show for choosing point size"""
    options = []
    # get list of all column names that aren't ints or floats
    for c in list(df):
        if df[c].dtype == 'int64' or df[c].dtype == 'float64':
            options.append({'label': c, 'value': c})
    return options


def strings_to_category_nums(arr, rescale=True, low=0, high=1):
    """Convert an array of strings to category integers.
    Example: ['a', 'b', 'c', 'a'] --> [0, 1, 2, 0].
    If rescale=True argument is used, integrers will be rescaled
    to floats between low and high."""
    a = pd.get_dummies(arr).values.argmax(1).astype('float')
    if rescale:
        a = (a - np.min(a)) / (np.max(a) - np.min(a))
        a = (a * (high - low)) + low
    return a
  
# get the options to show in the dropdown menus
plotting_options = get_plotting_options(df)
filtering_options = get_filtering_options(df)
point_size_options = get_point_size_options(df)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


import dash
import dash_core_components as dcc
import dash_html_components as html


# setup the server and app
app = dash.Dash(__name__)
app.title = TITLE
server = app.server  # this line is required for web hosting


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Put your Dash page layout code here

# create app layout
app.layout = html.Div([
    
    # top heading
    html.H1(children=TITLE),

    # paragraph for intro information
    
    html.P([
            html.B('Dataset: '), str(DATAPATH), html.Br(),
            html.B('Total rows: '), str(df.shape[0]), html.Br(),
            html.B('Total columns: '), str(df.shape[1]), html.Br(),
            ]),
    
    html.Hr(),







    # X dropdown menu
    html.P([html.B('Select a variable to plot on the X-axis'),]),

    dcc.Dropdown(
        id='x_var_dropdown',
        clearable=False,
        options=plotting_options,
        value=plotting_options[1]['value'],
        placeholder='Select variable for X-axis (optional)',
        style={'width': '60%', 'verticalAlign': 'middle'}),
    

    # Y dropdown menu
    html.P([html.B('Select a variable to plot on the Y-axis')]),

    dcc.Dropdown(
        id='y_var_dropdown',
        clearable=False,
        options=plotting_options,
        value=plotting_options[2]['value'],
        placeholder='Select variable for Y-axis',
        style={'width': '60%', 'verticalAlign': 'middle'}),
    
    html.Hr(),
    
    
    
 
    
    
    # filter dropdown menu
    html.P([html.B('Select a filter for the results')]),

    dcc.Dropdown(
        id='filter_dropdown',
        clearable=False,
        options=plotting_options,
        value=plotting_options[3]['value'],
        placeholder="Select variable for filtering",
        style={'width': '60%', 'verticalAlign': 'middle'}),   
    
    
    
    
    
    # filter value dropdown menu
    html.P([html.B('Select a value for the filter')]),

    dcc.Dropdown(
        id='filter_val_dropdown',
        clearable=False,
        placeholder="Select value for filtering",
        style={'width': '60%', 'verticalAlign': 'middle'}),
    
    html.Hr(),



 
    # point size dropdown menu
    html.P([html.B('Select a variable for the point size (optional)')]),

    dcc.Dropdown(
        id='point_size_dropdown',
        options=point_size_options,
        placeholder="Select variable for point size (optional)",
        style={'width': '60%', 'verticalAlign': 'middle'}),   
    
    # point color dropdown menu
    html.P([html.B('Select a variable for the point color (optional)')]),

    dcc.Dropdown(
        id='point_color_dropdown',
        options=plotting_options,
        placeholder="Select variable for point color (optional)",
        style={'width': '60%', 'verticalAlign': 'middle'}),   
    




    html.Hr(),




    # create plot
    dcc.Graph(id='graph', config={"displaylogo": False}),
    
    ])

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Create callbacks which animate page objects



@app.callback(
    dash.dependencies.Output('filter_val_dropdown', 'options'),
    [dash.dependencies.Input('filter_dropdown', 'value')])
def set_filter_val_options(selected_filter):
    """Set which options to show in the filter value dropdown menu"""
    filt_val_options = list(df.fillna('N/A')[selected_filter].unique())
    #filt_val_options = list(df[selected_filter].unique())                                              
    return [{'label': i, 'value': i} for i in filt_val_options]


@app.callback(
    dash.dependencies.Output('filter_val_dropdown', 'value'),
    [dash.dependencies.Input('filter_val_dropdown', 'options')])
def set_default_filter_val(available_options):
    """Populate the filter value dropdown menu with default value,
    using the first value as the default"""
    return available_options[0]['value']





# update graph
@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('x_var_dropdown', 'value'),
     dash.dependencies.Input('y_var_dropdown', 'value'),
     dash.dependencies.Input('filter_dropdown', 'value'),
     dash.dependencies.Input('filter_val_dropdown', 'value'),
     dash.dependencies.Input('point_size_dropdown', 'value'),
     dash.dependencies.Input('point_color_dropdown', 'value')])
def update_graph(X, Y, F, FV, PS, PC):
    """Update the graph when variable selections are changed"""
    
    '''
    
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



    '''
    
    
    dfs = df[df[F] == FV]#[[X, Y]].dropna()
    x = list(dfs[X])
    y = list(dfs[Y])


    
    # change point sizes based on selection in dropdown menu
    if PS is None:
        sizes = np.full(len(x), 20)
    else:
        sizes = np.nan_to_num(dfs[PS])
        if len(sizes) > 0:
            sizes = strings_to_category_nums(sizes, high=30, low=3)
    
    
    
    
    # change point colors based on selection in dropdown menu
    if PC is None:
        colors = np.full(len(x), 20)
    else:
        colors = np.nan_to_num(dfs[PC])

        if len(colors) > 0:
            colors = strings_to_category_nums(colors)





    # get lost of text to show when hovering over points
    hover_text = []
    for i in range(len(dfs)):
        vals = [it[1] for it in dfs.iloc[i].to_dict().items()][:5]
        hover_text.append(str(vals))
    
    
    # create list of data series to plot
    data_list = [
                {'x': x, 'y': y,
                 'text': hover_text,
                 'hoverinfo': 'text',
                 'mode': 'markers',
                 'marker': {'size': sizes,
                            'color': colors}}
                ]
    
    # create plot layout
    layout = {
        'title': 'Showing {} records where {} is {}'.format(len(dfs), format_var(F), FV),
        'xaxis': {'title': format_var(X)},
        'yaxis': {'title': format_var(Y)},
        'height': 800,
        'margin': {'l': 150, 'r': 150, 'b': 150, 't': 50}}


    return {'data': data_list, 'layout': layout}
            




             
if __name__ == '__main__':
    app.run_server(debug=False)
