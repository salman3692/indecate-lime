import pandas as pd
import plotly.graph_objects as go
import dash
import os
from dash import dcc, html, Input, Output

# -----------------------------
# Load the lime data
file_path = os.getenv('file_path', 'resultsPCupdated.csv')
data_df = pd.read_csv(file_path)

# Preprocessing: Create 'Technology' and 'Capture' columns
def classify_technology(conf):
    if 'NG' in conf:
        return 'NG'
    elif 'BioCH4' in conf:
        return 'BioCH4'
    elif 'Biomass' in conf:
        return 'Biomass'
    elif 'H2' in conf:
        return 'Hydrogen'
    elif 'Plasma' in conf:
        return 'Plasma'
    else:
        return 'Other'

def classify_capture(conf):
    if 'Oxy_CC' in conf:
        return 'Oxy Capture'
    elif '_CC' in conf:
        return 'MEA Capture'
    else:
        return 'No Capture'

data_df['Technology'] = data_df['configuration'].apply(classify_technology)
data_df['Capture'] = data_df['configuration'].apply(classify_capture)

# Keep only the relevant technologies
valid_technologies = ['NG', 'BioCH4', 'Biomass', 'Hydrogen', 'Plasma']
data_df = data_df[data_df['Technology'].isin(valid_technologies)]

# Mapping dictionaries
technology_mapping = {i+1: tech for i, tech in enumerate(valid_technologies)}
technology_reverse_mapping = {v: k for k, v in technology_mapping.items()}

capture_mapping = {'No Capture': 1, 'Oxy Capture': 2, 'MEA Capture': 3}
capture_reverse_mapping = {v: k for k, v in capture_mapping.items()}

# -----------------------------
external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@400;600&display=swap"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

# -----------------------------
# Helper for input blocks
def build_range_block(column, label, df):
    return html.Div([
        html.Label(label, style={'font-family': 'Familjen Grotesk, sans-serif'}),
        dcc.Input(id=f'{column}-min-input', type='number', value=df[column].min(),
                  style={'width': '70px', 'margin': '0 5px'}),
        dcc.Input(id=f'{column}-max-input', type='number', value=df[column].max(),
                  style={'width': '70px', 'margin': '0 5px'})
    ], style={'display': 'inline-block', 'margin': '10px'})

# -----------------------------
# Main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

def main_layout():
    return html.Div([

        html.Div([
            html.H3("Select one or more technologies to compare", style={
                'font-family': 'Familjen Grotesk, sans-serif',
                'text-align': 'left', 'margin-left': '42px', 'margin-bottom': '5px', 'color': '#003366'
            }),
            dcc.Checklist(
                id='Technology-toggle',
                options=[{'label': tech, 'value': tech} for tech in valid_technologies],
                value=valid_technologies,
                inline=True,
                style={'font-family': 'Familjen Grotesk, sans-serif', 'margin-left': '38px','margin-top': '20px','margin-bottom': '20px', 'display': 'flex', 'justify-content': 'left'}
            )
        ], style={'text-align': 'left'}),

        html.Div([
            html.H3("Select Prices of Energy Sources and Emissions below to create custom Scenarios", style={
                'font-family': 'Familjen Grotesk, sans-serif',
                'text-align': 'left', 'margin-left': '10px', 'margin-bottom': '5px', 'color': '#003366'
            }),

            build_range_block('cEE', 'Electricity Cost (€/MWh)', data_df),
            build_range_block('cH2', 'Hydrogen Cost (€/MWh)', data_df),
            build_range_block('cNG', 'NG Cost (€/MWh)', data_df),
            build_range_block('cBioCH4', 'Bio-CH₄ Cost (€/MWh)', data_df),
            build_range_block('cBiomass', 'Biomass Cost (€/MWh)', data_df),
            build_range_block('cCO2', 'CO₂ Cost (€/tCO₂)', data_df),
            build_range_block('cTS', 'CO₂ Transport & Storage Cost (€/tCO₂)', data_df)
        ], style={'text-align': 'left', 'margin-left': '30px'}),

        html.Div([
            dcc.Graph(id='parallel-coordinates-plot',
                      style={'width': '100%', 'height': '400px', 'margin': '0px'}),
            html.Div(id='percentage-relative-occurrence', style={'margin': '20px', 'font-family': 'Familjen Grotesk, sans-serif'})
        ], style={'padding': '20px', 'backgroundColor': '#ffffff'}),

        html.Footer([
            html.Div([
                html.P("Disclaimer: Results of INDECATE-Lime are based on simulations and open literature data. For discrepancies or unusual results, please contact m.salman@uliege.be.",
                    style={'font-size': '14px', 'font-family': 'Familjen Grotesk, sans-serif', 'color': '#6c757d', 'text-align': 'center', 'padding': '10px'})
            ], style={'backgroundColor': '#003366'})
        ])
    ])

# -----------------------------
# Routing
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    return main_layout()

# -----------------------------
# Main plot and percentage occurrence
@app.callback(
    Output('parallel-coordinates-plot', 'figure'),
    Output('percentage-relative-occurrence', 'children'),
    Input('Technology-toggle', 'value'),
    Input('cEE-min-input', 'value'), Input('cEE-max-input', 'value'),
    Input('cH2-min-input', 'value'), Input('cH2-max-input', 'value'),
    Input('cNG-min-input', 'value'), Input('cNG-max-input', 'value'),
    Input('cCO2-min-input', 'value'), Input('cCO2-max-input', 'value'),
    Input('cBioCH4-min-input', 'value'), Input('cBioCH4-max-input', 'value'),
    Input('cBiomass-min-input', 'value'), Input('cBiomass-max-input', 'value'),
    Input('cTS-min-input', 'value'), Input('cTS-max-input', 'value')
)
def update_plots(selected_techs, cEE_min, cEE_max, cH2_min, cH2_max, cNG_min, cNG_max, cCO2_min, cCO2_max, cBioCH4_min, cBioCH4_max, cBiomass_min, cBiomass_max, cTS_min, cTS_max):

    if not isinstance(selected_techs, list):
        selected_techs = [selected_techs]

    filtered_data = data_df[
        (data_df['Technology'].isin(selected_techs)) &
        (data_df['cEE'].between(cEE_min, cEE_max)) &
        (data_df['cH2'].between(cH2_min, cH2_max)) &
        (data_df['cNG'].between(cNG_min, cNG_max)) &
        (data_df['cCO2'].between(cCO2_min, cCO2_max)) &
        (data_df['cBioCH4'].between(cBioCH4_min, cBioCH4_max)) &
        (data_df['cBiomass'].between(cBiomass_min, cBiomass_max)) &
        (data_df['cTS'].between(cTS_min, cTS_max))
    ]

    total_count = filtered_data.shape[0]

    if total_count > 0:
        tech_counts = filtered_data['Technology'].value_counts()
        occurrence_info = []
        for tech, count in tech_counts.items():
            occurrence_info.append(
                html.Div([
                    html.Div([
                        html.H4(f"Technology: {tech}", style={'font-weight': 'bold', 'color': '#003366'}),
                        html.P(f"Number of occurrences: {count}", style={'font-size': '14px', 'color': '#333'})
                    ], style={'padding': '10px', 'backgroundColor': '#f8f9fa', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)', 'width': '200px'})
                ], style={'margin-right': '15px', 'flex-shrink': '0'})
            )

        scatter_data = [go.Scatter(
            x=[tech for tech in tech_counts.index],
            y=tech_counts.values,
            mode='lines+markers',
            marker=dict(size=10, color='blue', line=dict(width=2, color='darkblue')),
            line=dict(color='blue', width=2),
            name='Occurrences'
        )]

        scatter_layout = go.Layout(
            title='Number of Occurrences of Each Technology',
            xaxis=dict(title='Technology'),
            yaxis=dict(title='Number of Occurrences'),
            font=dict(family='Familjen Grotesk, sans-serif'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=20, t=50, b=50)
        )

        scatter_fig = go.Figure(data=scatter_data, layout=scatter_layout)

        percentage_occurrence = html.Div([
            html.H3("Details", style={'font-family': 'Familjen Grotesk, sans-serif', 'font-size': '22px', 'font-weight': 'bold', 'color': '#003366'}),
            html.P(f"Total number of solutions in the selected range: {total_count}", style={'font-size': '16px', 'color': '#495057'}),
            html.Br(),
            dcc.Graph(id='technology-occurrence-plot', figure=scatter_fig, style={'width': '100%', 'height': '400px'}),
            html.Br(),
            html.Div(occurrence_info, style={'display': 'flex', 'flex-wrap': 'wrap', 'gap': '15px', 'padding': '10px', 'justify-content': 'center'}),
        ], style={'margin-bottom': '20px', 'font-family': 'Familjen Grotesk, sans-serif'})

    else:
        percentage_occurrence = html.Div([
            html.H3("Details", style={'font-family': 'Familjen Grotesk, sans-serif', 'font-size': '22px', 'font-weight': 'bold', 'color': '#003366'}),
            html.P("No data available for the selected range.", style={'font-size': '16px', 'color': '#6c757d'})
        ], style={'margin-bottom': '20px', 'font-family': 'Familjen Grotesk, sans-serif'})

    fig = go.Figure(
        data=go.Parcoords(
            line=dict(color=[technology_reverse_mapping[c] for c in filtered_data['Technology']], colorscale='turbo'),
            dimensions=[
                dict(range=[data_df['cEE'].min(), data_df['cEE'].max()], tickvals=[10, 25, 50, 75, 100, 125, 150, 175],label='Electricity<br>(€/MWh)', values=filtered_data['cEE']),
                dict(range=[10,100], tickvals=[10, 25, 50, 75, 100],label='Hydrogen<br>(€/MWh)', values=filtered_data['cH2']),
                dict(range=[data_df['cNG'].min(), data_df['cNG'].max()], tickvals=[10, 35, 55, 75, 100], label='NG<br>(€/MWh)', values=filtered_data['cNG']),
                dict(range=[data_df['cBioCH4'].min(), data_df['cBioCH4'].max()], tickvals=[30, 50, 70, 90, 110], label='Bio-CH₄<br>(€/MWh)', values=filtered_data['cBioCH4']),
                dict(range=[data_df['cBiomass'].min(), data_df['cBiomass'].max()], tickvals=[20, 35, 50, 65, 80], label='Biomass<br>(€/MWh)', values=filtered_data['cBiomass']),
                dict(range=[data_df['cCO2'].min(), data_df['cCO2'].max()], tickvals=[75, 100, 150, 200, 250],label='CO₂<br>(€/kgCO₂)', values=filtered_data['cCO2']),
                dict(range=[data_df['cTS'].min(), data_df['cTS'].max()], tickvals=[25, 50, 75, 100], label='CO₂T&S<br>(€/kgCO₂)', values=filtered_data['cTS']),
                dict(range=[1,3], tickvals=[1,2,3], ticktext=['No Capture','Oxy Capture','MEA Capture'], label='Carbon Capture', values=[capture_mapping[c] for c in filtered_data['Capture']]),
                dict(range=[1,5], tickvals=list(technology_mapping.keys()), ticktext=list(technology_mapping.values()), label='Technology', values=[technology_reverse_mapping[c] for c in filtered_data['Technology']])
            ],
            unselected=dict(line=dict(color='green', opacity=0.0))
        )
    )

    fig.update_layout(
        title_font=dict(size=20, color='#003366'),
        font=dict(family='Familjen Grotesk, sans-serif', size=15),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=40, t=50, b=50)
    )

    return fig, percentage_occurrence

# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
