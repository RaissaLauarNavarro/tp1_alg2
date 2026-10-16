from auxiliares.geohash import gerarHash
tamanhoHash = 8


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

# ----------------------------------------------

def prefixoComum(string1, string2):
    tamanho = min(len(string1), len(string2))
    i = 0
    while i < tamanho and string1[i] == string2[i]:
        i += 1
    return i


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

        # adiciona o hash direto se não tiver filhos
        if filho is None:
            pai.filhos[caracteres[0]] = No(caracteres, [id])
            return
        
        # encontra o tamanho do prefixo em comum dos hashs
        prefixo = prefixoComum(filho.prefixo, caracteres)

        # verifica se todo o prefixo do filho esta no inicio do hash
        if prefixo == len(filho.prefixo):
            if prefixo == len(caracteres):
                filho.ids.append(id)
                return
        
            filho.ids.append(id)

            self.inserirCaractere(filho, caracteres[prefixo:], id)
            return

        # quando o prefixo comum é menor que o prefixo do filho
        # cria um nó intermediário entre os prefixos
        ids_temp = filho.ids + [id]
        temp = No(filho.prefixo[:prefixo], ids_temp)

        filho.prefixo = filho.prefixo[prefixo:]
        temp.filhos[filho.prefixo[0]] = filho

        nova_folha = No(caracteres[prefixo:], [id])
        temp.filhos[nova_folha.prefixo[0]] = nova_folha

        pai.filhos[caracteres[0]] = temp


    def buscarIds(self, caracteres):
        no = self.raiz
        resto = caracteres
        while resto:
            filho = no.filhos.get(resto[0])
            if filho is None:
                return []

            prefixo = prefixoComum(filho.prefixo, resto)

            if prefixo == len(resto):
                return filho.ids
            
            if prefixo < len(filho.prefixo):
                return []
            no = filho
            resto = resto[prefixo:]
        return no.ids


    def contarNos(self, no=None):
        if no is None:
            no = self.raiz
        total = 1
        for filho in no.filhos.values():
            total += self.contarNos(filho)
        return total

