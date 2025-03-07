import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import os
import glob

# Create a Dash application
app = dash.Dash(__name__)

# Folder path containing Excel files
folder_path = r"F:/GIS/Ownership/Sangli"

# Get all Excel files in the folder and its subfolders (recursive search)
excel_files = glob.glob(os.path.join(folder_path, "**", "*.xlsx"), recursive=True)

# Check if any Excel files were found
if not excel_files:
    raise FileNotFoundError(f"No Excel files found in the folder: {folder_path}")

# List to hold data from all Excel files
df_list = []

# Read and append data from all Excel files
for file in excel_files:
    try:
        data = pd.read_excel(file)
        df_list.append(data)
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Check if the df_list is empty after loading all files
if not df_list:
    raise ValueError("No data was loaded from the Excel files.")

# Concatenate all data into a single DataFrame
df = pd.concat(df_list, ignore_index=True)

# Pre-process the data to remove any unnecessary rows or columns and speed up the processing
df = df.dropna(subset=['District', 'Taluka', 'Village', 'Plot No.'])  # Remove rows with missing data in critical columns
districts = df['District'].unique()  # List of unique Districts

# Layout of the app
app.layout = html.Div([
    html.H1("Ownership Information"),

    # Store component to store district info
    dcc.Store(id='district-store'),

    # Dropdown for District selection
    html.Div([
        html.Label('Select District'),
        dcc.Dropdown(
            id='district-dropdown',
            options=[{'label': district, 'value': district} for district in districts],
            placeholder="Select a District"
        ),
    ]),

    # Dropdowns for District, Taluka, Village, Plot No.
    html.Div([
        html.Label('Select Taluka'),
        dcc.Dropdown(
            id='taluka-dropdown',
            placeholder="Select a Taluka",
            disabled=True,  # Disabled until District is selected
        )
    ]),

    html.Div([
        html.Label('Select Village'),
        dcc.Dropdown(
            id='village-dropdown',
            placeholder="Select a Village",
            disabled=True,  # Disabled until Taluka is selected
        )
    ]),

    html.Div([
        html.Label('Select Plot No.'),
        dcc.Dropdown(
            id='plot-dropdown',
            placeholder="Select a Plot No.",
            disabled=True,  # Disabled until Village is selected
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

# Callback to update the district store when a district is selected from the dropdown
@app.callback(
    Output('district-store', 'data'),
    [Input('district-dropdown', 'value')],
)
def update_district_store(selected_district):
    if selected_district:
        print(f"Selected District: {selected_district}")  # Debugging print
        return selected_district
    return None


# Callback to update Taluka dropdown based on selected District
@app.callback(
    Output('taluka-dropdown', 'options'),
    Output('taluka-dropdown', 'disabled'),
    Input('district-store', 'data')
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


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)