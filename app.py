import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import numpy as np
import pandas as pd
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.express as px
import cufflinks as cf



def non_cumulative(l):
    for i in range (len(l)-1, 0, -1):
        l[i] -= l[i-1]
    return l

def sort_by_country(country):
    temp_df = df[df['Country/Region'] == country]
    temp_df = temp_df.drop('Province/State', axis=1).drop('SNo', axis=1)
    temp_df = temp_df.groupby(['Country/Region', 'ObservationDate'], as_index=False).aggregate(['sum'], )
    temp_df.columns = df.columns[4:]
    temp_df= temp_df[temp_df['Confirmed'] != 0]
    temp_df['ConfirmedPerDay'] = non_cumulative(temp_df['Confirmed'].copy())
    temp_df['DeathsPerDay'] = non_cumulative(temp_df['Deaths'].copy())
    temp_df['RecoveredPerDay'] = non_cumulative(temp_df['Recovered'].copy())
    temp_df['Country'] = [country]*temp_df.shape[0]
    return temp_df



# df = pd.read_csv('./covid_19_data.csv')
df = pd.read_csv('./covid_19_data/covid_19_data.csv')
df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']
df['ObservationDate'] = pd.to_datetime(df['ObservationDate'])

df_country = sort_by_country(df['Country/Region'].value_counts().index[0])

for i in range(1, len(df['Country/Region'].value_counts())):
    temp = sort_by_country(df['Country/Region'].value_counts().index[i])
    df_country = pd.concat([df_country, temp])

df_country['Date'] = list(map(lambda x: x[1] ,df_country.index.values))
df_country = df_country.sort_index()

df['ConfirmedPerDay'] = non_cumulative(df['Confirmed'].copy())
df['DeathsPerDay'] = non_cumulative(df['Deaths'].copy())
df['RecoveredPerDay'] = non_cumulative(df['Recovered'].copy())

map_df = df_country.copy()
map_df['DateStr'] = map_df['Date'].apply(lambda x: str(x).split(' ')[0])
map_df.sort_values(by='Date', inplace=True)

print(map_df.columns)

app = dash.Dash()

mapOptions = [{'label': 'Confirmed', 'value': 'Confirmed'}, {'label': 'Deaths', 'value': 'Deaths'}, {'label': 'Active', 'value': 'Active'}, {'label': 'Recovered', 'value': 'Recovered'}]
countries = [{'label': country, 'value': country} for country in df_country['Country'].unique()]

app.layout = html.Div([
    html.H1('CoViD-19 Visualization.'),
    html.Div([
        html.H3('Select Type of Display : '),
        dcc.Dropdown( 
            id='mapsDispType',
            options=mapOptions,
            value='Confirmed',
            multi=False
        ),
        dcc.Graph(id="map-graph")
    ])
])

@app.callback(Output("map-graph", "figure"), [Input('mapsDispType', "value")])
def make_map(disp_map):
    return px.choropleth(map_df, locations="Country", 
                    locationmode='country names', color=disp_map, 
                    hover_name="Country", 
                    animation_frame='DateStr',
                    # color_continuous_scale="peach", 
                    title=f'Countries with {disp_map} Cases')


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8051', debug=True)