from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

list_lat =  [-80, -45, 0, 45, 80]
list_long = [0, 90, 180, 270]
date = '2019/12/23 00:00'
rad_path = 'rad/'

def transform_date(date_str, format1 = '%Y/%m/%d %H:%M', format2 = '%Y%m%d-%H%M'):
    date = datetime.strptime(date_str, format1)
    new_format_date = datetime.strftime(date, format2)
    return new_format_date

df = pd.DataFrame(np.arange(100.001, 2100.001, .001), columns= ['freq'])

for lat in list_lat:
    for long in list_long:
        name = f'{rad_path}rad_{lat}_{long}_{transform_date(date)}.csv'
        temp = pd.read_csv(name, names = ['freq', f'rad_{lat}_{long}', 'dummy'], header=0).drop(columns='dummy')
        df = df.merge(temp, on='freq', how='outer')

app = Dash()
app.layout = [
    html.H1(children = 'Plot of Martian Spectra', style={'textAlign':'center'}),
    dcc.Dropdown(df.columns[1:], 'rad_0_0', id='dropdown-selection'),
    dcc.Slider(100,2000,100,value=100,id='min-freq-slider'),
    dcc.Slider(200,2100,100,value=200,id='max-freq-slider'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('min-freq-slider', 'value'),
    Input('max-freq-slider', 'value')
)
def update_graph(yy, min_freq, max_freq):
    fig = px.line(df, x='freq', y=yy)
    fig.update_xaxes({'range': (min_freq, max_freq), 'autorange': False})
    return fig

if __name__ == '__main__':
    app.run(debug=True)