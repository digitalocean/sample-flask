class Reparto:
    destinos = []
    def __init__(self):
        pass
    
    def agregarDestino(self,destino):
        Reparto.destinos.append(destino)

    def eliminarDestino(self,destino):
        Reparto.destinos.remove(destino)

class Destino:
    def __init__(self,envio,latitud,longitud,direccion,localidad):
        self.direccionCompleta = direccion + ", " + localidad
        self.envio = envio
        self.latitud = latitud
        self.longitud = longitud
        self.cercano = None
        self.distanciaCercano = 0


