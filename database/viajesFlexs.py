class Viaje:
    numeroEnvio = None
    def __init__(self,fecha,comprador,numeroEnvio,direccion,localidad,vendedor,referemcia,estadoEnvio,motivo):
        self.fecha = fecha
        self.comprador = comprador
        self.numeroEnvio = numeroEnvio
        self.direccion = direccion
        self.localidad = localidad
        self.vendedor = vendedor
        self.referemcia = referemcia
        self.estadoEnvio = estadoEnvio
        self.motivo = motivo
        
def nuevoEnvio(fecha):
    pass