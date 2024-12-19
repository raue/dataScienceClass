# Import required libraries
import pandas as pd
import dash
# import dash_html_components as html
from dash import html
# import dash_core_components as dcc
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("002a_spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = ['All']   # shall be default according to Task 1, therefore must be an additional entry in list
for site in spacex_df['Launch Site'].unique():
    launch_sites.append(site)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                  id='site-dropdown',
                                  # options=[{"label":site_dropdown, "value": site_dropdown} for site_dropdown in spacex_df["Launch Site"].unique()],
                                  options=[{"label":site_dropdown, "value": site_dropdown} for site_dropdown in launch_sites],
                                  value='All',
                                  placeholder='Select a Site.'
                                  ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                dcc.Graph(id="success-pie-chart"),
                                html.Br(),

                                # html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(min = spacex_df['Payload Mass (kg)'].min(), max = 10000, step = 1000, value = [1000, 5000] , id='payload-slider', marks={i: '{}'.format(i) for i in range(0, 10001, 1000)}),
                                # html.Div(id='output-container-range-slider'),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
  Output(component_id='success-pie-chart', component_property='figure'),
  Input(component_id='site-dropdown',component_property='value')
  )
def update_pie_chart(site_dropdown):
  # Pie w/ counts
  if site_dropdown == 'All':
    success_launches = spacex_df[spacex_df['class'] == 1]
    success_launches_data = success_launches.groupby('Launch Site')['class'].sum().reset_index()
    success_launches_data.rename(columns={'class': 'Count'}, inplace=True)
    fig = px.pie(success_launches_data, values = 'Count',
                    names = 'Launch Site',
                    title = 'Successfull Launches by Site').update_traces(textinfo='value') # https://stackoverflow.com/questions/61384947/how-to-display-values-in-numbers-instead-of-precentages-in-plotly-pie-chart

  else:
    site_launches = spacex_df[spacex_df['Launch Site'] == site_dropdown]
    fails = site_launches['class'].value_counts()[0]
    successes = site_launches['class'].value_counts()[1]
    site_df =pd.DataFrame({'Counts': [successes,fails], 'Type' :['Success', 'Failed']})
    fig = px.pie(site_df, values = 'Counts',
                    names = 'Type',
                    title = f'Launches by Site: {site_dropdown}').update_traces(textinfo='value')
  return fig


  # Pie w/ percentage:
  # if site_dropdown == 'All':
  #       fig = px.pie(values=spacex_df.groupby('Launch Site')['class'].mean(),
  #                    names=spacex_df.groupby('Launch Site')['Launch Site'].first(),
  #                    title='Total Success Launches by Site')
  # else:
  #     fig = px.pie(values=spacex_df[spacex_df['Launch Site']==str(site_dropdown)]['class'].value_counts(normalize=True),
  #                   names=spacex_df['class'].unique(),
  #                   title='Total Success Launches for Site {}'.format(site_dropdown))
  # return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Add a scatter chart to show the correlation between payload and launch success
@app.callback(
  Output('success-payload-scatter-chart', 'figure'),
  [Input('payload-slider', 'value'), Input(component_id='site-dropdown',component_property='value')]
  )
def update_output(value, site_dropdown):
  payload_min = value[0]
  payload_max = value[1]
  if site_dropdown == 'All':
    fig = px.scatter(spacex_df[spacex_df['Payload Mass (kg)'].between(payload_min, payload_max)],
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            hover_data=['Launch Site'],
            title='Reporting Launch Success vs Payload for All Sites')
  else:
    df = spacex_df[spacex_df['Launch Site']==str(site_dropdown)]
    fig = px.scatter(df[df['Payload Mass (kg)'].between(payload_min, payload_max)],
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            hover_data=['Launch Site'],
            title='Reporting Launch Success vs Payload for Site {}'.format(site_dropdown))
  return(fig)


# Run the app
if __name__ == '__main__':
    app.run_server()
