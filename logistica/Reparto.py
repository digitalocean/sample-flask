class Reparto:
    def __init__(self):
        self.destinos = []
    
    def agregarDestino(self,destino):
        self.destinos.append(destino)

    def eliminarDestino(self,destino):
        self.destinos.remove(destino)
