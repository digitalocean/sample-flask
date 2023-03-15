from abc import ABC, abstractmethod



class Strategy(ABC):
    @abstractmethod
    def facturar_viajes(self, viajes,sobreEscribe):
        pass


class EnCaminoStrategy(Strategy):
    def facturar_viajes(self, viajes,sobreEscribe=False):
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
    def facturar_viajes(self, viajes,sobreEscribe=False):
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
    def facturar_viajes(self, viajes,sobreEscribe=False):
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
        if len(no_se_cobran) > 0 and sobreEscribe:
            from Backend.database.database import connect_db
            midb = connect_db()
            cursor = midb.cursor()
            no_se_cobran = tuple(no_se_cobran)
            sql = f"update historial_estados set Precio = 0,Costo = 0 where Numero_envío in {no_se_cobran}"
            cursor.execute(sql)
            midb.commit()
        return total,viajes2
    

class PorVisitaStrategy:
    def facturar_viajes(self, viajes,sobreEscribe=False):
        facturas = {}
        total_a_cobrar = 0
        viajes2 = []
        for viaje in viajes:
            if viaje.estado_envio in ["Entregado"] or viaje.motivo in ["Nadie en domicilio", "Rechazado"]:
                if viaje.Direccion not in facturas:
                    facturas[viaje.Direccion] = {"visitas": 1, "precio_unitario": viaje.Precio_Cliente, "precio_total": viaje.Precio_Cliente}
                    precio = viaje.Precio_Cliente
                else:
                    facturas[viaje.Direccion]["visitas"] += 1
                    facturas[viaje.Direccion]["precio_total"] += viaje.Precio_Cliente * 0.7
                    precio = viaje.Precio_Cliente * 0.7
                precio_viaje = viaje.Precio_Cliente if viaje.estado_envio == "Entregado" else viaje.Precio_Cliente * 0.7
                informacion_viaje = (viaje.Fecha, viaje.Numero_envío, viaje.Direccion, viaje.Localidad, precio, viaje.comprador, precio_viaje, viaje.estadoActual)
                viajes2.append(informacion_viaje)
                total_a_cobrar += precio_viaje
        return total_a_cobrar, viajes2
