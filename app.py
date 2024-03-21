# Import dependencies
from dash import Dash, html, dcc, Input, Output 
import pandas as pd
import plotly.express as px
import dash

# Read in the data from the CSV file
df = pd.read_csv("gdp_pcap.csv")

# function to convert 'k' values to numeric
def convert_to_numeric(value):
    if isinstance(value, str) and value[-1] == 'k':
        return float(value[:-1]) * 1000
    elif isinstance(value, int):
        return value
    else:
        return float(value)

# Convert 'k' values to numeric, excluding the 'country' column
df.iloc[:, 1:] = df.iloc[:, 1:].applymap(convert_to_numeric)

# Load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Initialize app
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server

# Define layout and elements
app.layout = html.Div([
    html.H1("GDP per Capita for Various Countries Over the Years"),  # Title
    html.P("The app shows the GDP per capita of various countries over time using a graph and an interactive dropdown menu and slider. Each country is represented by a different color on the graph and the associated trends in the GDP are reflected for each of the years. The dropdown can be used to select a particular country while the slider can be used to filter out certain dates."),  # Description
    # Dropdown element
    html.Div([
        html.Label('Country Dropdown'),
        dcc.Dropdown(
            id='country',
            options=[{"label": x, "value": x} for x in sorted(df["country"].unique())], 
            placeholder='Select a country',
            multi=True,
            style={'width':'100%'}
        )
    ], style={'width': '50%', 'display': 'inline-block'}),
    # Slider component
    html.Div([
        html.Label('Select Year Range:'),
        dcc.RangeSlider(
            id='range-slider-1',
            min=int(df.columns[1]), 
            max=int(df.columns[-1]),
            step=1, 
            marks={i: str(i) if i % 50 == 0 else '' for i in range(int(df.columns[1]), int(df.columns[-1])+1)},
            value=[int(df.columns[1]), int(df.columns[-1])],
            tooltip={'placement': 'bottom', 'always_visible': True}
        )
    ], style={'width': '50%', 'display': 'inline-block', 'float': 'right'}),
    # Graph component
    html.Div([
        dcc.Graph(
            id='gdp-graph',
            figure=px.line(
                pd.melt(df, id_vars=['country'], var_name='year', value_name='gdpPercap'),
                x='year',
                y='gdpPercap',
                color='country',
                title='GDP Per Capita Over Time',
                labels={'year': 'Year', 'gdpPercap': 'GDP Per Capita'}
            )
        )
    ],style={'width':'100%'}),
])

# Callback function to update the graph based on dropdown selection and slider selection
@app.callback(
    Output('gdp-graph', 'figure'),
    [Input('country', 'value'),
     Input('range-slider-1', 'value')]
)
def update_graph(selected_countries, selected_years):
    # Initialize filtered dataframe
    filtered_df = df.copy()

    # Apply dropdown filter
    if selected_countries:
        filtered_df = df[df['country'].isin(selected_countries)]

    # Apply slider filter
    if selected_years:
        start_year, end_year = selected_years
        # Exclude the 'country' column from filtering
        filtered_df = filtered_df.loc[:, ['country'] + [col for col in df.columns if col.isdigit() and int(col) >= start_year and int(col) <= end_year]]

    return px.line(
        pd.melt(filtered_df, id_vars=['country'], var_name='year', value_name='gdpPercap'),
        x='year',
        y='gdpPercap',
        color='country',
        title='GDP Per Capita Over Time',
        labels={'year': 'Year', 'gdpPercap': 'GDP Per Capita'}
    )



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
