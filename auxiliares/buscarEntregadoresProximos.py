import pandas as pd
from math import radians, cos, sin, asin, sqrt
from auxiliares.geohash import gerarHash

tamanho_hash = 40
raio_terra = 6371
km_cada_grau = 110.5


def buscarEntregadores(tree, posicoes, raio, lat, lon):
    # calcula o tamanho da celula do geohash para gerar o prefixo de busca 
    for tamanhoPrefixo in range(tamanho_hash, 0, -1):
        alturac = 180 / 2 ** (tamanhoPrefixo * 5 // 2)
        largurac = 360 / 2 ** ((tamanhoPrefixo * 5 + 1) // 2)

        alturakm = alturac * km_cada_grau
        largurakm = largurac * km_cada_grau * cos(radians(lat))

        if min(alturakm, largurakm) >= raio:
            break

    prefixos_celulas = set()

    # gera os prefixos das celulas ao redor do restaurante para fazer a procura
    for ilat in (-1, 0, 1):
        for ilon in (-1, 0, 1):
            latitude = lat + ilat * alturac
            longitude = lon + ilon * largurac

            hash = gerarHash(latitude, longitude)
            prefixos_celulas.add(hash[:tamanhoPrefixo])

    # pega os entregadores que estão nessas células 
    entregadores = []
    for prefixo in prefixos_celulas:
        entregadores.extend(tree.buscarIds(prefixo))

    entregadoresVermelho = []
    entregadoresCinza = []

    for entregador in entregadores:
        elat, elon = posicoes[entregador]
        dlat = radians(elat - lat)
        dlon = radians(elon - lon)

        # calcula o a da formula de haversine
        a = (sin(dlat / 2) ** 2+ cos(radians(lat))* cos(radians(elat)) * sin(dlon / 2) ** 2)
        distanciakm = 2 * raio_terra * asin(sqrt(a))

        entregador = (entregador, distanciakm)

        if distanciakm <= raio:
            entregadoresVermelho.append(entregador)
        else:
            entregadoresCinza.append(entregador)

    # ordena os entregadores pela distancia entre ele e o resaurante
    entregadoresVermelho.sort(key=lambda entregador: entregador[1])
    entregadoresCinza.sort(key=lambda entregador: entregador[1])

    return entregadoresVermelho, entregadoresCinza