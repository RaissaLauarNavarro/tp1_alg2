from geohash import gerarHash
tamanhoHash = 8


def prefixo_comum(prefixo1, prefixo2):
    tamanho = min(len(prefixo1), len(prefixo2))
    i = 0
    while i < tamanho and prefixo1[i] == prefixo2[i]:
        i += 1
    return i


class No:
    def __init__(self, prefixo, ids=None):
        self.prefixo = prefixo
        self.filhos = {}
        if ids is None:
            self.ids = []
        else:
            self.ids = ids

    def efolha(self):
        return not self.filhos


class Tree:
    def __init__(self):
        self.raiz = No("", None)


    def limpar(self):
        self.raiz = No("", None)


    def inserirNo(self, id, lat, lon):
        hash = gerarHash(lat, lon, tamanhoHash)
        self.inserirCaractere(self.raiz, hash, id)


    def inserirCaractere(self, pai, caracteres, id):
        filho = pai.filhos.get(caracteres[0])

        # Cria um novo nó pai
        if filho is None:
            pai.filhos[caracteres[0]] = No(caracteres, [id])
            return

        prefixo = prefixo_comum(filho.prefixo, caracteres)

        if prefixo == len(filho.prefixo):
            if filho.efolha():
                filho.ids.append(id)
            else:
                self.inserirCaractere(filho, caracteres[prefixo:], id)
            return
        
        temp = No(filho.prefixo[:prefixo], None)
        filho.prefixo = filho.prefixo[prefixo:]
        temp.filhos[filho.prefixo[0]] = filho
        nova_folha = No(caracteres[prefixo:], [id])
        temp.filhos[nova_folha.prefixo[0]] = nova_folha
        pai.filhos[caracteres[0]] = temp


    def buscarPrefixo(self, caracteres):
        no = self.raiz
        resto = caracteres
        while resto:
            filho = no.filhos.get(resto[0])
            if filho is None:
                return []

            prefixo = prefixo_comum(filho.prefixo, resto)
            if prefixo == len(resto):
                return self.obterIds(filho)
            
            if prefixo < len(filho.prefixo):
                return []
            no = filho
            resto = resto[prefixo:]
        return self.obterIds(no)


    def obterIds(self, no):
        if no.efolha():
            return list(no.ids)
        encontrados = []
        for filho in no.filhos.values():
            encontrados.extend(self.obterIds(filho))
        return encontrados


    def contarNos(self, no=None):
        if no is None:
            no = self.raiz
        total = 1
        for filho in no.filhos.values():
            total += self.contarNos(filho)
        return total
