from distutils.log import debug
from turtle import color
import weakref
import dash  # biblioteca que gerencia o dashboard
from dash import dcc
from dash import html  # permite o uso de codigos html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px  # criação de gráficos
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json

# lendo o dataset
# df = pd.read_csv("HIST_COVIDBR_13mai2021.csv", sep=";")

# # como o df é muito grande, irei dividir estados e país
# df_states = df[(~df["estado"].isna()) & (df["codmun"].isna())]
# df_brasil = df[df["regiao"] == "Brasil"]

# #salvando o arquivo localmente
# df_states.to_csv("df_states.csv")
# df_brasil.to_csv("df_brasil.csv")

# lendo os arquivos criado localmente
df_states = pd.read_csv("df_states.csv")
df_brasil = pd.read_csv("df_brasil.csv")

# lendo arquivo geojson
brasil_geo = json.load(open("geojson/brazil_geo.json", "r"))

df_data = df_states[df_states["estado"] == "RJ"]

select_columns = {"casosAcumulado": "Casos Acumulados",
                  "casosNovos": "Novos Casos",
                  "obitosAcumulado": "Óbitos Totais",
                  "obitosNovos": "Óbitos por dia"}

df_states_day = df_states[df_states["data"] == "2020-05-13"]

# instanciando o dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# criando uma figura que irá conter o gráfico do mapa do brasil
fig = px.choropleth_mapbox(df_states_day, locations="estado", color="casosNovos",
                           center={"lat": -16.95, "lon": -47.78}, zoom=3,
                           geojson=brasil_geo, color_continuous_scale="Redor", opacity=0.4,
                           hover_data={"casosAcumulado": True, "casosNovos": True, "obitosNovos": True, "estado": True})

fig.update_layout(
    paper_bgcolor="#242424",
    autosize=True,
    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
    showlegend=False,
    mapbox_style="carto-darkmatter"
)

# grafico de barras
fig2 = go.Figure(layout={"template": "plotly_dark"})
fig2.add_trace(go.Scatter(x=df_data["data"], y=df_data["casosAcumulado"]))

fig2.update_layout(
    paper_bgcolor="#242424",
    plot_bgcolor="#242424",
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10)
)


# construção do layout
app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            # aqui vai a logo e o subtitulo da logo
            html.Div([
                html.Img(id="logo", src=app.get_asset_url(
                    "logo_covid.png"), height=80, width=120),
                html.H5("Evolução COVID-19"),
                dbc.Button("BRASIL", color="primary",
                           id="location-button", size="lg")
            ], style={}),
            html.P("Informe a data na qual deseja obter as informações:",
                   style={"margin-top": "40px"}),
            # aqui vai o seletor de data (datepicker)
            html.Div(id="div-teste", children=[
                dcc.DatePickerSingle(
                    id="date-picker",
                    min_date_allowed=df_brasil["data"].min(),
                    max_date_allowed=df_brasil["data"].max(),
                    initial_visible_month=df_brasil["data"].min(),
                    date=df_brasil["data"].max(),
                    display_format="MMMM, D, YYYY",
                    style={"boder": "0px solid black"}
                )
            ]),

            dbc.Row([
                dbc.Col([
                    # aqui vai o primeiro card
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos Recuperados"),
                            html.H3(style={"color": "#adfc92"},
                                    id="casos-recuperados-text"),
                            html.Span("Em acompanhamento"),
                            html.H5(id="em-acompanhamento-text"),
                        ])
                    ], color="light", outline=True, style={"margin-top": "10px",
                                                           "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                                           "color": "#FFFFFF"}),
                ], md=4),
                dbc.Col([
                    # aqui vai o segundo card
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos Confirmados"),
                            html.H3(style={"color": "#389fd6"},
                                    id="casos-confirmados-text"),
                            html.Span("Novos casos na data"),
                            html.H5(id="novos-casos-text"),
                        ])
                    ], color="light", outline=True, style={"margin-top": "10px",
                                                           "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                                           "color": "#FFFFFF"}),
                ], md=4),
                dbc.Col([
                    # aqui vai o terceiro card
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Óbitos Confirmados"),
                            html.H3(style={"color": "#DF2935"},
                                    id="obitos-text"),
                            html.Span("Óbitos na data"),
                            html.H5(id="obitos-na-data-text"),
                        ])
                    ], color="light", outline=True, style={"margin-top": "10px",
                                                           "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                                           "color": "#FFFFFF"}),
                ], md=4),
            ]),
            # aqui vai a opção de selecionar os dados e o grafico de linhas
            html.Div([
                html.P("Selecione o tipo de dado que deseja visualizar:",
                       style={"margin-top": "25px"}),
                dcc.Dropdown(id="location-dropdaw",
                             options=[{"label": j, "value": i}
                                      for i, j in select_columns.items()],
                             value="casosNovos",
                             style={"margin-top": "10px"}),
                dcc.Graph(id="line-graph", figure=fig2)

            ]),
        ], md=6, style={"padding": "25px", "background_color": "#242424"}),
        # aqui vai o grafico do brasil
        dbc.Col([
            dcc.Loading(id="loading-1", type="default",
                        children=[dcc.Graph(id="choropleth-map", figure=fig,
                                            style={"height": "100vh", "margin-right": "10px"})
                                  ]),
        ], md=6)
    ]), fluid=True)

# interatividades com o dashboard
@app.callback(
    [
        Output("casos-recuperados-text", "children"),
        Output("em-acompanhamento-text", "children"),
        Output("casos-confirmados-text", "children"),
        Output("novos-casos-text", "children"),
        Output("obitos-text", "children"),
        Output("obitos-na-data-text", "children"),
    ],
    [Input("date-picker", "date"), Input("location-button", "children")]
    )
def display_status(date, location):
    if location == "BRASIL":
        df_data_on_date = df_brasil[df_brasil["data"] == date]
    else:
        df_data_on_date = df_states[(df_states["estado"] == location) & (df_states["data"] == date)]
    
    recuperados_novos = "-" if df_data_on_date["Recuperadosnovos"].isna().values[0] else f'{int(df_data_on_date["Recuperadosnovos"].values[0]):,}'.replace(",", ".") 
    acompanhamentos_novos = "-" if df_data_on_date["emAcompanhamentoNovos"].isna().values[0]  else f'{int(df_data_on_date["emAcompanhamentoNovos"].values[0]):,}'.replace(",", ".") 
    casos_acumulados = "-" if df_data_on_date["casosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["casosAcumulado"].values[0]):,}'.replace(",", ".") 
    casos_novos = "-" if df_data_on_date["casosNovos"].isna().values[0]  else f'{int(df_data_on_date["casosNovos"].values[0]):,}'.replace(",", ".") 
    obitos_acumulado = "-" if df_data_on_date["obitosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["obitosAcumulado"].values[0]):,}'.replace(",", ".") 
    obitos_novos = "-" if df_data_on_date["obitosNovos"].isna().values[0]  else f'{int(df_data_on_date["obitosNovos"].values[0]):,}'.replace(",", ".") 
    return (
            recuperados_novos, 
            acompanhamentos_novos, 
            casos_acumulados, 
            casos_novos, 
            obitos_acumulado, 
            obitos_novos,
            )


if __name__ == "__main__":
    app.run_server(debug=True)
