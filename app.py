import pandas as pd
import dash
import dash_leaflet as dl
import osmnx as ox
from dash import html, Output, Input, dash_table, dcc, State
from dash.dash_table.Format import Format, Scheme
from auxiliares.simularGeracaoEntregadores import simulaGeracaoEntregadores
from auxiliares.descomprime_grafo import descomprime_grafo
from auxiliares.buscaCoordenadasBar import busca_coordenadas_bar
from auxiliares.tree import Tree
# verificar se vai manter abrir o navegador sozinho
from threading import Timer
import webbrowser


coordenada_central = (-19.9191, -43.9386)
arquivo_bares = "data/bares_com_coordenadas.csv"
arquivo_mapa_bh = "data/grafo_bh.graphml"
n_padrao = 20
icone_vermelho = {
    "iconUrl": "https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png",
    "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    "iconSize": [25, 41],
    "iconAnchor": [12, 41],
    "tooltipAnchor": [16, -28],
    "shadowSize": [41, 41],
}


def carregar_nomes(arquivo_bares):
    bares = pd.read_csv(arquivo_bares, dtype=str, keep_default_na=False)
    
    fantasia = bares["NOME_FANTASIA"].str.strip()
    # se o nome fantasia tiver somente caracteres especiais, usa o nome jurídico para identificação do bar
    fantasia = fantasia.where(fantasia.str.contains(r"[^\W_]"), "")
    nome =fantasia.where(fantasia != "", bares["NOME"].str.strip())
    bairro = bares["NOME_BAIRRO"].str.strip()
    desc_logradouro = bares["DESC_LOGRADOURO"].str.strip()
    logradouro = bares["NOME_LOGRADOURO"].str.strip()
    numero = bares["NUMERO_IMOVEL"].str.strip()
    bares["item"] = nome.where(bairro == "", nome + " - " + bairro + " (" + desc_logradouro + " " + logradouro + ", " + numero + ")")

    primeira = nome.str[:1]
    bares["grupo"] = 0
    bares.loc[~primeira.str.isalnum(), "grupo"] = 1
    bares.loc[(fantasia == "") & primeira.str.isdigit(), "grupo"] = 2

    bares = bares.sort_values(["grupo", "item", "_id"])
    return [{"label": item, "value": id_bar} for item, id_bar in zip(bares["item"], bares["_id"])]

opcoes_bares = carregar_nomes(arquivo_bares)
descomprime_grafo()
grafo = ox.load_graphml(arquivo_mapa_bh)
arvoreEntregadores = Tree()

app = dash.Dash()
app.layout = html.Div(className="app", children=[
    html.Aside(className="painel", children=[
        html.H1("Localizador de entregadores"),
        html.Label("Bares e restaurantes:"),

        dcc.Dropdown(
            id="dropdown-bar",
            className="input",
            options=opcoes_bares,
            placeholder="Selecione um bar ou restaurante...",
        ),

        html.Label("Raio de filtragem:"),
        dcc.Slider(id="raio", min=0.5, max=2, step=0.5, value=1, marks={0.5: "0,5", 1: "1", 1.5: "1,5", 2: "2",},),

        html.Label("Quantidade de entregadores disponíveis:"),
        dcc.Input(id="input-qtd-entregadores", type="number", value=n_padrao, className="input"),
        html.Button("Gerar Entregadores", id="botao-gerar-entregadores", className="botao", n_clicks=0),
    ]),

    html.Main(className="main", children=[

        html.Div(className="div_mapa", children=[
            dl.Map(id="mapa", center=coordenada_central, zoom=13, preferCanvas=True, className="mapa", children=[
                dl.TileLayer(
                    url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    maxZoom=19,
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                ),
                dl.LayerGroup(id="camada"),
            ]),
        ]),
 
        html.Section(className="section_tabela", children=[
            dash_table.DataTable(
                columns=[
                    {"name": "ID Entregador", "id": "id", "type": "numeric"},
                    {"name": "Distância (km)", "id": "dist", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed, decimal_delimiter=",")},
                    {"name": "Tempo (min)", "id": "eta", "type": "numeric", "format": Format(precision=1, scheme=Scheme.fixed, decimal_delimiter=",")},
                ],
                data=[],
                page_size=10,
                sort_action="native",
                style_as_list_view=True,
            ),
        ]),
    ]),
])


# Callback pra ele ficar escutando quando o usuario selecionar um bar ou clickar no botao de gerar entregadores
@app.callback(
    Output("camada", "children"),
    Output("mapa", "center"),
    Input("botao-gerar-entregadores", "n_clicks"),
    Input("dropdown-bar", "value"),
    State("input-qtd-entregadores", "value"),
    prevent_initial_call=True
)


# Funcão a ser chamada ao selecionar um bar ou clicar em gerar entregadores
def atualizar_entregadores(n_clicks, bar_selecionado_id, qtd_entregadores):
    if not bar_selecionado_id:
        return [], dash.no_update
    lat, long = busca_coordenadas_bar(bar_selecionado_id)
    localizacao_restaurante = {"latitude": float(lat), "longitude": float(long)}
    posicao_restaurante = [localizacao_restaurante["latitude"], localizacao_restaurante["longitude"]]

    marcadores = []
    arvoreEntregadores.limpar()

    # Um marker vermelho pro restaurante
    marcadores.append(
        dl.Marker(
            position=posicao_restaurante,
            icon=icone_vermelho,
            children=[dl.Tooltip("Restaurante Selecionado")]
        )
    )

    # Se só selecionou o bar, mostra apenas ele e centraliza o mapa
    if dash.ctx.triggered_id == "dropdown-bar" or not qtd_entregadores:
        return marcadores, posicao_restaurante

    entregadores = simulaGeracaoEntregadores(qtd_entregadores, localizacao_restaurante, grafo)

    # Adiciona os marcadores dos entregadores gerados
    for i, entregador in enumerate(entregadores):
        id_entregador = i+1
        entregador["id"] = id_entregador
        arvoreEntregadores.inserirNo(id_entregador, entregador["latitude"], entregador["longitude"]) 
        marcadores.append(
            dl.Marker(
                position=[entregador["latitude"], entregador["longitude"]],
                children=[dl.Tooltip(f"Entregador {id_entregador}")]
            )
        )
        
    return marcadores, dash.no_update


if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open_new("http://127.0.0.1:8050/")).start()
    app.run(host="127.0.0.1", port=8050, debug=False)


