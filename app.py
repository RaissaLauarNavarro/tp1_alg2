import csv
import dash
import dash_leaflet as dl
from dash import html, Output, Input, dash_table, dcc
from dash.dash_table.Format import Format, Scheme


# verificar se vai manter abrir o navegador sozinho
from threading import Timer
import webbrowser


coordenada_central = (-19.9191, -43.9386)
arquivo_bares = "data/bares.csv"
n_padrao = 20


def carregar_nomes(arquivo_bares):
    opcoes = []
    with open(arquivo_bares, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            fantasia = linha["NOME_FANTASIA"].strip()
            nome = fantasia or linha["NOME"].strip()
            bairro = linha["NOME_BAIRRO"].strip()
            item = f"{nome} - {bairro}" if bairro else nome
            if not fantasia and nome[:1].isdigit():
                grupo = 2
            elif not nome[:1].isalnum():
                grupo = 1
            else:
                grupo = 0
            opcoes.append((grupo, item, linha["_id"]))
    opcoes.sort()
    return [{"label": item, "value": id_bar} for _, item, id_bar in opcoes]

opcoes_bares = carregar_nomes(arquivo_bares)


app = dash.Dash()
app.layout = html.Div(className="app", children=[
    html.Aside(className="painel", children=[
        html.H1("Localizador de entregadores"),
        html.Label("Bares e restaurantes:"),

        dcc.Dropdown(
            className="input",
            options=opcoes_bares,
            placeholder="Selecione um bar ou restaurante...",
        ),

        html.Label("Raio de filtragem:"),
        dcc.Slider(id="raio", min=0.5, max=2, step=0.5, value=1, marks={0.5: "0,5", 1: "1", 1.5: "1,5", 2: "2",},),

        html.Label("Quantidade de entregadores disponíveis:"),
        dcc.Input(type="number", value=n_padrao, className="input"),
        html.Button("Gerar Entregadores", className="botao"),
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


if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open_new("http://127.0.0.1:8050/")).start()
    app.run(host="127.0.0.1", port=8050, debug=False)


