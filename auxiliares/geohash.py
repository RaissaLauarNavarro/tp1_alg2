alfabeto = "0123456789bcdefghjkmnpqrstuvwxyz"
indice = {}
for i, c in enumerate(alfabeto):
    indice[c] = i
niveis_padrao = 8


def codificar(latitude, longitude, niveis=niveis_padrao):
    maior_latitude = 90.0
    menor_latitude = -90.0
    maior_longitude = 180.0
    menor_longitude = -180.0
    tamanho = niveis * 5
    geohash = []

    for i in range(tamanho):
        if i % 2 == 0:
            meio = (menor_longitude + maior_longitude) / 2
            if longitude >= meio:
                geohash.append(1)
                menor_longitude = meio
            else:
                geohash.append(0)
                maior_longitude = meio
        else:
            meio = (menor_latitude + maior_latitude) / 2
            if latitude >= meio:
                geohash.append(1)
                menor_latitude = meio
            else:
                geohash.append(0)
                maior_latitude = meio

    geohash_final = ""
    for i in range(0, tamanho, 5):
        numero = 0
        for bit in geohash[i:i + 5]:
            numero = numero * 2 + bit
        geohash_final += alfabeto[numero]
    return geohash_final


def decodificar(geohash_final):
    maior_latitude = 90.0
    menor_latitude = -90.0
    maior_longitude = 180.0
    menor_longitude = -180.0
    tamanho = len(geohash_final) * 5
    geohash = []

    for i in geohash_final:
        numero = indice[i]
        for j in range(4, -1, -1):
            geohash.append((numero >> j) & 1)

    for i in range(tamanho):
        if i % 2 == 0:
            meio = (menor_longitude + maior_longitude) / 2
            if geohash[i] == 1:
                menor_longitude = meio
            else:
                maior_longitude = meio
        else:
            meio = (menor_latitude + maior_latitude) / 2
            if geohash[i] == 1:
                menor_latitude = meio
            else:
                maior_latitude = meio

    latitude = (menor_latitude + maior_latitude) / 2
    longitude = (menor_longitude + maior_longitude) / 2
    return latitude, longitude