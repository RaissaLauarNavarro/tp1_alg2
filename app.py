
from dash import Dash
import dash
import dash_leaflet as dl
import webbrowser
from dash import html, Output, Input, dash_table, dcc

# verificar se vai manter abrir o navegador sozinho
from threading import Timer



app = Dash()
app.layout = html.Div(className="app", children=[
    html.Aside(className="painel", children=[
        html.H1("Localizdor de entregdores"),
        html.Label("Restaurante:"),
        dcc.Dropdown(
            id="restaurante-dropdown",
            options=[
                {"label": "Restaurante A", "value": "A"},
                {"label": "Restaurante B", "value": "B"},
                {"label": "Restaurante C", "value": "C"},
            ],
            value="A",
        ),
    ])
])


if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open_new("http://127.0.0.1:8050/")).start()
    app.run(host="127.0.0.1", port=8050, debug=False)


