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
        no_se_cobran = []
        viajes2 = []
        for viaje in viajes:
            if viaje.estado_envio == "En Camino":
                if viaje.Fecha in direcciones and f"{viaje.Direccion}, {viaje.Localidad}" == direcciones[viaje.Fecha]:
                    no_se_cobran.append(viaje.Numero_envío)
                    viajes2.append([viaje.Fecha, viaje.Numero_envío,viaje.Direccion,viaje.Localidad,
                         0,viaje.comprador,viaje.Cobrar,viaje.estadoActual])
                    continue    
                total += viaje.Precio_Cliente
                direcciones[viaje.Fecha] = f"{viaje.Direccion}, {viaje.Localidad}"
                viajePack = [viaje.Fecha, viaje.Numero_envío,viaje.Direccion,viaje.Localidad,
                            viaje.Precio_Cliente,viaje.comprador,viaje.Cobrar,viaje.estadoActual]
                viajes2.append(viajePack)
                
        from Backend.database.database import connect_db
        midb = connect_db()
        cursor = midb.cursor()
        no_se_cobran = tuple(no_se_cobran)
        print(no_se_cobran)
        sql = f"update historial_estados set Precio = 0,Costo = 0 where Numero_envío in {no_se_cobran}"
        cursor.execute(sql)
        midb.commit()
        return total,viajes2