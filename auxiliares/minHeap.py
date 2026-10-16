class MinHeap:
    # vamos usar aquilo de guardar o heap como array simulando uma arvore binaria
    # Ai um filho é a posicao * 2 + 1 e o outro é posicao * 2 + 2
    def __init__(self):
        self.heap = []

    def vazio(self):
        return len(self.heap) == 0

    def push(self, item):
        self.heap.append(item)
        self.sobe_na_arvore(len(self.heap) - 1)

    def pop(self):
        if self.vazio():
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        menor_item = self.heap[0]
        
        self.heap[0] = self.heap.pop()
        self.desce_na_arvore(0)
        
        return menor_item

    def sobe_na_arvore(self, index):
        pai = (index - 1) // 2
        while index > 0 and self.heap[index][0] < self.heap[pai][0]:
            self.heap[index], self.heap[pai] = self.heap[pai], self.heap[index]
            index = pai
            pai = (index - 1) // 2

    def desce_na_arvore(self, index):
        tamanho = len(self.heap)
        while True:
            filho_esquerdo = 2 * index + 1
            filho_direito = 2 * index + 2
            menor = index

            if filho_esquerdo < tamanho and self.heap[filho_esquerdo][0] < self.heap[menor][0]: 
                menor = filho_esquerdo

            if filho_direito < tamanho and self.heap[filho_direito][0] < self.heap[menor][0]:
                menor = filho_direito

            # Só para de descer na arvore binaria quando estiver na posição certa
            if menor != index:
                self.heap[index], self.heap[menor] = self.heap[menor], self.heap[index]
                index = menor
            else:
                break
