from abc import ABC, abstractmethod



class Strategy(ABC):
    @abstractmethod
    def facturar_viajes(self, viajes):
        pass


class EnCaminoStrategy(Strategy):
    def facturar_viajes(self, viajes):
        total = 0
        viajes2 = []
        for viaje in viajes:
            if viaje.estado_envio == "En Camino":
                total += viaje.Precio_Cliente
            viajes2.append([viaje.Fecha, 
            viaje.Numero_envío,
            viaje.Direccion,
            viaje.Localidad,
            viaje.Precio_Cliente,
            viaje.comprador,
            viaje.Cobrar,
            viaje.estadoActual])
        return total,viajes2
    

class EntregadoStrategy(Strategy):
    def facturar_viajes(self, viajes):
        total = 0
        viajes2 = []
        for viaje in viajes:
            if viaje.estado_envio == "Entregado":
                total += viaje.Precio_Cliente
                viajes2.append([viaje.Fecha, 
                viaje.Numero_envío,
                viaje.Direccion,
                viaje.Localidad,
                viaje.Precio_Cliente,
                viaje.comprador,
                viaje.Cobrar,
                viaje.estadoActual])
        return total,viajes2
    

class EnCaminoUnicoStrategy(Strategy):
    def facturar_viajes(self, viajes):
        total = 0
        direcciones = {}
        viajes2 = []
        for viaje in viajes:
            if viaje.estado_envio == "En Camino":
                if viaje.Fecha in direcciones and f"{viaje.Direccion}, {viaje.Localidad}" == direcciones[viaje.Fecha]:
                    viaje.Precio_Cliente = 0
                    viajePack = [viaje.Fecha, viaje.Numero_envío,viaje.Direccion,viaje.Localidad,
                         0,viaje.comprador,viaje.Cobrar,viaje.estadoActual]
                    viajes2.append(viajePack)
                    continue    
                total += viaje.Precio_Cliente
                direcciones[viaje.Fecha] = f"{viaje.Direccion}, {viaje.Localidad}"
                viajePack = [viaje.Fecha, viaje.Numero_envío,viaje.Direccion,viaje.Localidad,
                            viaje.Precio_Cliente,viaje.comprador,viaje.Cobrar,viaje.estadoActual]
                viajes2.append(viajePack)
        return total,viajes2