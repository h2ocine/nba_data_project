import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import statsmodels.api as sm
import os
import utils
# Charger les données team_stats et standings
team_stats_path = "../data/teams_stats/NBA-Team-Regular-Season-Stats-{}.csv"
standings_path = "../data/standings/NBA-Standings-Regular-Season-{}.csv"

team_stats = utils.load_all_data_teams(team_stats_path, 2002)
standings = utils.load_all_data_teams(standings_path, 2002)

# Renommer les colonnes pour correspondre
team_stats = team_stats.rename(columns={'Team Name': 'Team'})
standings = standings.rename(columns={'Team Name': 'Team'})

# Joindre les deux jeux de données sur les colonnes Team et Year
combined_df = pd.merge(team_stats, standings, on=['Team', 'Year'])

# Vérifier si les colonnes 'Rank' et 'W' existent dans combined_df
if 'Rank' not in combined_df.columns or 'W' not in combined_df.columns:
    raise KeyError("Les colonnes 'Rank' ou 'W' ne sont pas présentes dans les données combinées.")

# Sélectionner les colonnes d'intérêt
columns_of_interest_stats = ['GP', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OR', 'DR', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF']
column_of_interest_standing = ['PPG', 'OPP PPG', 'DIFF', 'HOME-W', 'HOME-L', 'AWAY-W', 'AWAY-L', 'DIV-W', 'DIV-L', 'CONF-W', 'CONF-L', 'Last10-W', 'Last10-L']
column_of_must_have = ['Rank', 'W']

# Créer les colonnes combinées
combined_df['HOME'] = combined_df['HOME-W'] + combined_df['HOME-L']
combined_df['AWAY'] = combined_df['AWAY-W'] + combined_df['AWAY-L']
combined_df['DIV'] = combined_df['DIV-W'] + combined_df['DIV-L']
combined_df['CONF'] = combined_df['CONF-W'] + combined_df['CONF-L']

selected_columns_df_stats = combined_df[columns_of_interest_stats + column_of_must_have]
selected_columns_df_standing = combined_df[column_of_interest_standing + ['HOME', 'AWAY', 'DIV', 'CONF'] + column_of_must_have]

# Créer l'application Dash
app = dash.Dash(__name__)
app.title = "NBA Team Performance Dashboard"

app.layout = html.Div([
    html.Div([
        html.H1("NBA Team Performance Dashboard", style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '20px'}),
    ], style={'backgroundColor': '#1E1E1E', 'padding': '20px'}),
    html.Div([
        html.Label("Select Year Range:", style={'color': '#FFFFFF', 'marginRight': '20px'}),
        html.Div([
            dcc.RangeSlider(
                id='year-slider',
                min=2002,
                max=2023,
                marks={str(year): str(year) for year in range(2002, 2024)},
                step=1,
                value=[2010, 2012],
                tooltip={"placement": "bottom", "always_visible": True},
                included=True
            ),
        ], style={'width': '80%', 'display': 'inline-block'}),
        html.Label("Select Statistic Type:", style={'color': '#FFFFFF', 'marginLeft': '20px', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='stat-type-dropdown',
            options=[
                {'label': 'Team Stats', 'value': 'team_stats'},
                {'label': 'Standings Stats', 'value': 'standings_stats'}
            ],
            value='team_stats',
            style={'width': '200px', 'display': 'inline-block'}
        ),
    ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'backgroundColor': '#333333', 'padding': '20px', 'borderRadius': '10px'}),
    html.Div([
        html.Label("Select Variables:", style={'color': '#FFFFFF', 'marginRight': '20px'}),
        dcc.Checklist(
            id='variable-checklist',
            options=[{'label': var, 'value': var} for var in columns_of_interest_stats + column_of_interest_standing],
            value=columns_of_interest_stats,
            inline=True,
            style={'color': '#FFFFFF'}
        ),
    ], style={'margin': '20px'}),
    dcc.Tabs([
        dcc.Tab(label='Correlation Analysis', children=[
            html.Div([
                dcc.Graph(id='correlation-heatmap'),
            ], style={'margin': '20px'}),
            html.Div([
                dcc.Graph(id='correlation-barplot-w'),
            ], style={'margin': '20px'}),
            html.Div([
                dcc.Graph(id='correlation-barplot-rank'),
            ], style={'margin': '20px'}),
        ]),
        dcc.Tab(label='Regression Analysis', children=[
            html.Div([
                dcc.Graph(id='regression-importance-plot'),
            ], style={'margin': '20px', 'backgroundColor': '#2E2E2E', 'padding': '20px', 'borderRadius': '10px'})
        ]),
    ]),
], style={'width': '80%', 'margin': 'auto', 'backgroundColor': '#2E2E2E', 'padding': '20px', 'borderRadius': '10px'})

@app.callback(
    [Output('correlation-heatmap', 'figure'),
     Output('correlation-barplot-w', 'figure'),
     Output('correlation-barplot-rank', 'figure'),
     Output('regression-importance-plot', 'figure'),
     Output('variable-checklist', 'value')],
    [Input('year-slider', 'value'),
     Input('stat-type-dropdown', 'value'),
     Input('variable-checklist', 'value')],
    [State('stat-type-dropdown', 'value')]
)
def update_graphs(selected_years, stat_type, selected_variables, current_stat_type):
    start_year, end_year = selected_years

    if stat_type == 'team_stats':
        filtered_df = selected_columns_df_stats[(combined_df['Year'] >= start_year) & (combined_df['Year'] <= end_year)]
        default_variables = columns_of_interest_stats
        columns_to_include = [col for col in selected_variables if col in columns_of_interest_stats]
    else:
        filtered_df = selected_columns_df_standing[(combined_df['Year'] >= start_year) & (combined_df['Year'] <= end_year)]
        default_variables = column_of_interest_standing + ['HOME', 'AWAY', 'DIV', 'CONF']
        columns_to_include = [col for col in selected_variables if col in default_variables]

    if not columns_to_include:  # Si aucune colonne n'est sélectionnée, utiliser les colonnes par défaut
        columns_to_include = default_variables

    if filtered_df.empty:
        print(f"No data available for the selected range: {start_year}-{end_year}")
        return {}, {}, {}, {}, []

    correlation_matrix = filtered_df.corr()

    # Heatmap
    heatmap_fig = px.imshow(correlation_matrix, aspect="auto",
                            title=f'Correlation Matrix ({start_year}-{end_year})', color_continuous_scale='RdBu_r', zmin=-1, zmax=1)

    # Bar plot des corrélations avec les victoires (W)
    correlation_with_w = correlation_matrix['W'].drop('W')
    barplot_w_fig = go.Figure()
    barplot_w_fig.add_trace(go.Bar(
        x=correlation_with_w.index,
        y=correlation_with_w.values,
        marker_color=correlation_with_w.values,
        marker_colorscale='RdBu_r',
        hovertemplate='%{x}: %{y:.2f}<extra></extra>',
    ))
    barplot_w_fig.update_layout(title='Corrélations entre les Statistiques et les Victoires (W)',
                                xaxis_title='Statistiques',
                                yaxis_title='Corrélation',
                                coloraxis_showscale=True)

    # Bar plot des corrélations avec le rang (Rank)
    correlation_with_rank = correlation_matrix['Rank'].drop('Rank')
    barplot_rank_fig = go.Figure()
    barplot_rank_fig.add_trace(go.Bar(
        x=correlation_with_rank.index,
        y=-1 * correlation_with_rank.values,
        marker_color=-1 * correlation_with_rank.values,
        marker_colorscale='RdBu_r',
        hovertemplate='%{x}: %{y:.2f}<extra></extra>',
    ))
    barplot_rank_fig.update_layout(title='Corrélations entre les Statistiques et le Rang',
                                   xaxis_title='Statistiques',
                                   yaxis_title='Corrélation',
                                   coloraxis_showscale=True)

    # Regression Analysis
    X = filtered_df[columns_to_include]
    y = filtered_df['Rank']

    # Ajouter une constante (intercept) pour la régression
    X = sm.add_constant(X)

    # Ajuster le modèle de régression linéaire
    model = sm.OLS(y, X).fit()

    # Importance des Variables (Basé sur les Coefficients Absolus)
    params = model.params.drop('const')
    pvalues = model.pvalues.drop('const')
    importance = params.abs()

    importance_fig = go.Figure()
    importance_fig.add_trace(go.Bar(
        x=importance.index,
        y=importance.values,
        marker_color=params.values,
        marker_colorscale='Viridis',
        text=[f'p-value: {pv:.4f}' for pv in pvalues.values],
        hovertemplate='%{x}: %{y:.2f}<br>%{text}<extra></extra>',
    ))
    importance_fig.update_layout(title='Importance des Variables (Régression)',
                                 xaxis_title='Variables',
                                 yaxis_title='Valeur Absolue des Coefficients',
                                 coloraxis_showscale=True)

    return heatmap_fig, barplot_w_fig, barplot_rank_fig, importance_fig, columns_to_include

if __name__ == '__main__':
    app.run_server(debug=True)
