import pandas as pd
import dash
import dash_leaflet as dl
import osmnx as ox
from dash import html, Output, Input, dash_table, dcc, State
from dash.dash_table.Format import Format, Scheme
from auxiliares.tree import Tree
from auxiliares.descomprime_grafo import descomprime_grafo
from auxiliares.buscaCoordenadasBar import getCoordenadasBar
from auxiliares.simularGeracaoEntregadores import simulaGeracaoEntregadores
from auxiliares.buscarEntregadoresProximos import buscarEntregadores
from auxiliares.tempoEntrega import tempoEntrega, tempoEntregas
# verificar se vai manter abrir o navegador sozinho
from threading import Timer
import webbrowser


arquivo_bares = "data/bares_com_coordenadas.csv"
arquivo_mapa_bh = "data/grafo_bh.graphml"
coordenada_central = (-19.9191, -43.9386)


icone_vermelho = {
    "iconUrl": f"https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png",
        "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
        "iconSize": [25, 41],
        "iconAnchor": [12, 41],
        "tooltipAnchor": [16, -28],
        "shadowSize": [41, 41],
}
icone_azul = {
    "iconUrl": f"https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-blue.png",
        "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
        "iconSize": [25, 41],
        "iconAnchor": [12, 41],
        "tooltipAnchor": [16, -28],
        "shadowSize": [41, 41],
}
icone_cinza = {
    "iconUrl": f"https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-grey.png",
        "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
        "iconSize": [25, 41],
        "iconAnchor": [12, 41],
        "tooltipAnchor": [16, -28],
        "shadowSize": [41, 41],
}


def criarMarcadorEntregador(id_entregador, posicao, icone):
    return dl.Marker(
        position=list(posicao),
        icon=icone,
        children=[dl.Tooltip(f"Entregador {id_entregador}")]
    )


def carregarNomes(arquivo_bares):
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


# ------------------------------------------------------------------------------------------------------------


opcoes_bares = carregarNomes(arquivo_bares)
descomprime_grafo()
grafo = ox.load_graphml(arquivo_mapa_bh)
arvoreEntregadores = Tree()
coordenadasEntregadores = {}

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
        html.Label("Quantidade de entregadores disponíveis:"),
        dcc.Input(id="input-qtd-entregadores", type="number", value=20, className="input"),
        html.Button("Gerar Entregadores", id="botao-gerar-entregadores", className="botao", n_clicks=0),

        html.Label("Raio de filtragem (km):"),
        dcc.Input(id="raio", type="number", value=2.0, min=0.1, step=0.1, className="input"),
        html.Button("Filtrar Entregadores", id="botao-filtrar-entregadores", className="botao", n_clicks=0),
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
                id="tabela-entregadores",
                columns=[
                    {"name": "ID Entregador", "id": "id", "type": "numeric"},
                    {"name": "Distância linha reta (km)", "id": "dist", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed, decimal_delimiter=",")},
                    {"name": "Tempo (min)", "id": "eta", "type": "numeric", "format": Format(precision=1, scheme=Scheme.fixed, decimal_delimiter=",")},
                    {"name": "Distância no grafo (km)", "id": "distreal", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed, decimal_delimiter=",")},
                ],
                data=[],
                page_action="none",
                fixed_rows={"headers": True},
                style_table={"maxHeight": "35vh", "overflowY": "auto"},
                sort_action="native",
                style_as_list_view=True,

                style_data_conditional=[
                    {"if": {"filter_query": '{cor} = "vermelho"'}, "color": "#d33"},
                    {"if": {"filter_query": '{cor} = "cinza"'}, "color": "#888"},
                ]
            ),
        ]),
    ]),
])


# Callback pra ele ficar escutando quando o usuario selecionar um bar ou clickar no botao de gerar entregadores
@app.callback(
    Output("camada", "children"),
    Output("mapa", "center"),
    Output("tabela-entregadores", "data"),
    Input("botao-gerar-entregadores", "n_clicks"),    
    Input("botao-filtrar-entregadores", "n_clicks"),
    Input("dropdown-bar", "value"),
    State("input-qtd-entregadores", "value"),
    State("raio", "value"),
    prevent_initial_call=True
)


# Funcão a ser chamada ao selecionar um bar ou clicar em gerar entregadores
def atualizar_entregadores(n_gerar, n_clicks, bar_selecionado_id, qtd_entregadores, raio):
    if not bar_selecionado_id:
        return [], dash.no_update, []
    lat, long = getCoordenadasBar(bar_selecionado_id)
    localizacao_restaurante = {"latitude": float(lat), "longitude": float(long)}
    posicao_restaurante = [localizacao_restaurante["latitude"], localizacao_restaurante["longitude"]]

    # Um marker azul pro restaurante
    marcadores = [
        dl.Marker(
            position=posicao_restaurante,
            icon=icone_azul,
            children=[dl.Tooltip("Restaurante Selecionado")]
        )
    ]

    # Mostra o bar selecionado no centro do mapa
    if dash.ctx.triggered_id == "dropdown-bar":
        arvoreEntregadores.limpar()
        coordenadasEntregadores.clear()
        return marcadores, posicao_restaurante, []

    # Botao gerar: cria novos entregadores e mostra todos em cinza, ainda sem filtrar
    if dash.ctx.triggered_id == "botao-gerar-entregadores":
        if not qtd_entregadores:
            return marcadores, dash.no_update, []

        arvoreEntregadores.limpar()
        coordenadasEntregadores.clear()
        entregadores = simulaGeracaoEntregadores(qtd_entregadores, localizacao_restaurante, grafo)

        for i, entregador in enumerate(entregadores):
            id_entregador = i + 1
            entregador["id"] = id_entregador
            coordenadasEntregadores[id_entregador] = (entregador["latitude"], entregador["longitude"])
            arvoreEntregadores.inserirNo(id_entregador, entregador["latitude"], entregador["longitude"])
            marcadores.append(criarMarcadorEntregador(id_entregador, coordenadasEntregadores[id_entregador], icone_cinza))

        return marcadores, dash.no_update, []

    if not coordenadasEntregadores or not raio or raio <= 0:
        return dash.no_update, dash.no_update, dash.no_update

    entregadoresVermelho, entregadoresCinza = buscarEntregadores(arvoreEntregadores, coordenadasEntregadores, raio, localizacao_restaurante["latitude"], localizacao_restaurante["longitude"])
    entregadoresVFormatados = []
    for entregadorV in entregadoresVermelho:
        entregadoresVFormatados.append(coordenadasEntregadores[entregadorV[0]])
    tempo_entregas, distancia_entregas = tempoEntregas(entregadoresVFormatados, localizacao_restaurante, grafo)
    for i, tempo_entrega in enumerate(tempo_entregas):
        entregadoresVermelho[i] += (tempo_entrega/60,distancia_entregas[i]/1000)
    entregadoresCFormatados = []
    for entregadorC in entregadoresCinza:
        entregadoresCFormatados.append(coordenadasEntregadores[entregadorC[0]])
    tempo_entregas, distancia_entregas = tempoEntregas(entregadoresCFormatados, localizacao_restaurante, grafo)
    for i, tempo_entrega in enumerate(tempo_entregas):
        entregadoresCinza[i] += (tempo_entrega/60,distancia_entregas[i]/1000)
    idsVermelhos = {id_entregador for id_entregador, _,_,_ in entregadoresVermelho}
    for id_entregador, posicao in coordenadasEntregadores.items():
        if id_entregador in idsVermelhos:
            icone = icone_vermelho
        else:
            icone = icone_cinza
        marcadores.append(criarMarcadorEntregador(id_entregador, posicao, icone))

    tabela = (
        [{"id": id_entregador, "dist": distancia, "eta": tempo_minutos, "cor": "vermelho", "distreal": distancia_no_grafo} for id_entregador, distancia, tempo_minutos, distancia_no_grafo in entregadoresVermelho] +
        [{"id": id_entregador, "dist": distancia, "eta": tempo_minutos, "cor": "cinza", "distreal": distancia_no_grafo} for id_entregador, distancia, tempo_minutos, distancia_no_grafo in entregadoresCinza]
    )
    
    return marcadores, dash.no_update, tabela




if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open_new("http://127.0.0.1:8050/")).start()
    app.run(host="127.0.0.1", port=8050, debug=False)


