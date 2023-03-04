class Destino:
    def __init__(self,envio,latitud,longitud,direccion,localidad):
        self.direccionCompleta = direccion + ", " + localidad
        self.envio = envio
        self.latitud = latitud
        self.longitud = longitud
        self.cercano = None
        self.distanciaCercano = 0

