# Trabalho Prático 1 Algoritmos 2 - Indexação Geoespacial e Geometria Computacional Híbrida

## Estrutura dos arquivos
* app.py : arquivo main do projeto, com a construção da interface do app
* documentacao_tp1.pdf : documentação do trabalho com explicações e testes
* requeriments.txt : arquivo usado para baixar as bibliotecas necessárias
* \data : pasta com os arquivos necessários, como o csv de bares/restaurantes e do grafo de bh 
* \auxiliares : pasta com os scipts de funcionamento do projeto
* \assets : pasta necessária para a definição do visual da página

## Instruções de execução

- faça a instalação do python 3.12 pelo site oficial (versão necessária para as bibliotecas)
- abra a pasta do projeto
- crie um ambiente virtual que utilize o python 3.12 e instale as bibiotecas necessárias com os comandos:
```sh
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
- execute o programa:
```sh
.\.venv\Scripts\python.exe app.py
```
- abra no navegador a porta em que o programa iniciou:

http://localhost:8050

obs: espere a inicialização completa do aplicativo (quando todos os componentes aparem, como a caixa de seleção)

o título da página será Updating enquando os resultados estão sendo carregados