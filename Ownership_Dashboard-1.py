import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Create a Dash application
app = dash.Dash(__name__)

# Load the Excel file only once during the app startup
df = pd.read_excel(r"F:/GIS/Quantasip/Maharashtra Ownership/05 अकोला/02 आकोट/Akolkhed.xlsx")

# Pre-process the data to remove any unnecessary rows or columns and speed up the processing
df = df.dropna(subset=['District', 'Taluka', 'Village', 'Plot No.'])  # Remove rows with missing data in critical columns
districts = df['District'].unique()  # List of unique Districts

# Layout of the app
app.layout = html.Div([
    html.H1("7/12 Information"),

    # Dropdowns for District, Taluka, Village, Plot No.
    html.Div([
        html.Label('Select District'),
        dcc.Dropdown(
            id='district-dropdown',
            options=[{'label': district, 'value': district} for district in districts],
            placeholder="Select a District",
            style={'animation': 'none'}
        )
    ]),

    html.Div([
        html.Label('Select Taluka'),
        dcc.Dropdown(
            id='taluka-dropdown',
            placeholder="Select a Taluka",
            disabled=True,  # Disabled until District is selected
            style={'animation': 'none'}
        )
    ]),

    html.Div([
        html.Label('Select Village'),
        dcc.Dropdown(
            id='village-dropdown',
            placeholder="Select a Village",
            disabled=True,  # Disabled until Taluka is selected
            style={'animation': 'none'}
        )
    ]),

    html.Div([
        html.Label('Select Plot No.'),
        dcc.Dropdown(
            id='plot-dropdown',
            placeholder="Select a Plot No.",
            disabled=True,  # Disabled until Village is selected
            style={'animation': 'none'}
        )
    ]),

    # Button to show plot information
    html.Div([
        html.Button('Show Plot Info', id='show-info-button', n_clicks=0)
    ]),

    # Display Plot Info
    html.Div(id="plot-info-display"),

    # "Dashboard made by Onkar Keskar" in the bottom-right
    html.Div(
        "Dashboard made by Onkar Keskar",
        style={
            'position': 'fixed',
            'bottom': '10px',
            'right': '10px',
            'font-family': 'Times New Roman',
            'font-size': '14px',
            'color': 'black',
            'z-index': '9999'
        }
    ),
])

# Callback to update Taluka dropdown based on selected District
@app.callback(
    Output('taluka-dropdown', 'options'),
    Output('taluka-dropdown', 'disabled'),
    Input('district-dropdown', 'value')
)
def set_taluka_options(selected_district):
    if selected_district:
        # Filter Taluka values based on District selection
        filtered_df = df[df['District'] == selected_district]
        talukas = filtered_df['Taluka'].unique()
        options = [{'label': taluka, 'value': taluka} for taluka in talukas]
        return options, False  # Enable Taluka dropdown
    return [], True  # Disable Taluka dropdown if no District is selected


# Callback to update Village dropdown based on selected Taluka
@app.callback(
    Output('village-dropdown', 'options'),
    Output('village-dropdown', 'disabled'),
    Input('taluka-dropdown', 'value')
)
def set_village_options(selected_taluka):
    if selected_taluka:
        # Filter Village values based on Taluka selection
        filtered_df = df[df['Taluka'] == selected_taluka]
        villages = filtered_df['Village'].unique()
        options = [{'label': village, 'value': village} for village in villages]
        return options, False  # Enable Village dropdown
    return [], True  # Disable Village dropdown if no Taluka is selected


# Callback to update Plot No. dropdown based on selected Village
@app.callback(
    Output('plot-dropdown', 'options'),
    Output('plot-dropdown', 'disabled'),
    Input('village-dropdown', 'value')
)
def set_plot_options(selected_village):
    if selected_village:
        # Filter Plot No. values based on Village selection
        filtered_df = df[df['Village'] == selected_village]
        plots = filtered_df['Plot No.'].unique()
        options = [{'label': plot, 'value': plot} for plot in plots]
        return options, False  # Enable Plot No. dropdown
    return [], True  # Disable Plot No. dropdown if no Village is selected


# Callback to display Plot Info when 'Show Plot Info' button is clicked
@app.callback(
    Output('plot-info-display', 'children'),
    Input('plot-dropdown', 'value'),
    Input('show-info-button', 'n_clicks')
)
def display_plot_info(selected_plot, n_clicks):
    if selected_plot and n_clicks > 0:
        # Filter Plot Info based on selected Plot No.
        filtered_df = df[df['Plot No.'] == selected_plot]
        plot_info = filtered_df['Plot Info'].iloc[0]  # Get the Plot Info from Column E
        return html.Div([
            html.H3(f"Plot Info for Plot No. {selected_plot}"),
            html.P(plot_info)
        ])
    return ""  # Return empty if no Plot No. is selected or button is not clicked

# Callback to change color of selected dropdown
@app.callback(
    Output('district-dropdown', 'style'),
    Output('taluka-dropdown', 'style'),
    Output('village-dropdown', 'style'),
    Output('plot-dropdown', 'style'),
    Input('district-dropdown', 'value'),
    Input('taluka-dropdown', 'value'),
    Input('village-dropdown', 'value'),
    Input('plot-dropdown', 'value'),
)
def change_dropdown_color(district_value, taluka_value, village_value, plot_value):
    selected_style = {'backgroundColor': 'lightgreen', 'animation': 'color-change 1s ease'}
    default_style = {'animation': 'none'}

    district_style = selected_style if district_value else default_style
    taluka_style = selected_style if taluka_value else default_style
    village_style = selected_style if village_value else default_style
    plot_style = selected_style if plot_value else default_style

    return district_style, taluka_style, village_style, plot_style


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

