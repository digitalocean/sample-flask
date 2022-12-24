import time
from datetime import datetime
from geopy.distance import geodesic
from database import database
import mysql.connector
from .script import geocoder
class Envio:
    def __init__(self,numeroEnvio,direccion,localidad,vendedor,comprador=None,telefono=None,referencia=None,cp=None,fecha=datetime.now(),numeroVenta=None,chofer=None,observacion=None,
                motivo=None,precio=None,costo=None,scanner=None,estadoEnvio="Lista Para Retirar",fotoDomicilio=None,firma=None,tipoEnvio=None,latitud=None,longitud=None,correoChofer=None,
                ultimoMotivo=None,recibeOtro=None,fotoDni=None,cobrar=None,reprogramaciones=None,col1=None,col2=None,fromDB=False):
        
        if not fromDB:
            midb = database.connect_db()
            cursor = midb.cursor()
            cursor.execute('''select "Listo para salir (Sectorizado)" from retirado where Numero_envío = %s 
                            union
                            select "Retirado" from retirado where Numero_envío = %s 
                            ''',(numeroEnvio,numeroEnvio))
            estado = cursor.fetchone()
            if estado != None:
                self.estado_envio = estado[0]
            else:
                self.estado_envio = estadoEnvio
        else:
            self.estado_envio = estadoEnvio
        chars = '.,!"#$%&/()=?¡¿'
        self.Numero_envío = numeroEnvio.translate(str.maketrans('', '', chars))
        direccionCompleta = direccion + ", " + localidad + ", buenos aires"
        if type(latitud) == None or type(longitud) == None:
            print("geolocaliza")
            latlong = geocoder(direccionCompleta)
            self.Latitud = latlong[0]
            self.Longitud = latlong[1]
        else:
            self.Latitud = latitud
            self.Longitud = longitud

        self.Check = None
        self.Zona = None
        self.Fecha = fecha
        self.nro_venta = numeroVenta
        self.comprador = comprador
        self.Telefono = telefono
        self.Direccion = direccion
        self.Referencia = referencia
        self.Localidad = localidad
        self.capital = None
        self.CP = cp
        self.Vendedor = vendedor
        self.Chofer = chofer
        self.Observacion = observacion
        self.Motivo = motivo
        self.Direccion_Completa = direccionCompleta 
        self.Currentlocation = None
        self.Timechangestamp = None        
        self.Precio_Cliente = precio
        self.Precio_Chofer = costo
        self.Scanner = scanner
        self.Foto_domicilio = fotoDomicilio
        self.Firma_Entregado = None
        self.tipo_envio = tipoEnvio
        self.Correo_chofer = correoChofer
        self.Ultimo_motivo = ultimoMotivo
        self.Recibe_otro = recibeOtro
        self.Foto_dni = fotoDni
        self.Cobrar = cobrar
        self.Reprogramaciones = reprogramaciones
        self.Columna1 = col1
        self.Columna2 = col2

    def toDB(self):
        midb = database.connect_db()
        cursor = midb.cursor()
        
        sql = """insert into ViajesFlexs (`Check`,Zona,Fecha,Numero_envío,nro_venta,comprador,Telefono,
            Direccion,Referencia,Localidad,capital,CP,Vendedor,Chofer,Observacion,Motivo,Direccion_Completa,Currentlocation,
            Timechangestamp,Latitud,Longitud,Precio_Cliente,Precio_Chofer,Scanner,estado_envio,Foto_domicilio,Firma_Entregado,
            tipo_envio,Correo_chofer,Ultimo_motivo,Recibe_otro,Foto_dni,Cobrar,Reprogramaciones,`Columna 1`,`Columna 2`)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (self.Check,self.Zona,self.Fecha,self.Numero_envío,self.nro_venta,self.comprador,
                    self.Telefono,self.Direccion,self.Referencia,self.Localidad,self.capital,self.CP,
                    self.Vendedor,self.Chofer,self.Observacion,self.Motivo,self.Direccion_Completa,
                    self.Currentlocation,self.Timechangestamp,self.Latitud,self.Longitud,self.Precio_Cliente,
                    self.Precio_Chofer,self.Scanner,self.estado_envio,self.Foto_domicilio,self.Firma_Entregado,
                    self.tipo_envio,self.Correo_chofer,self.Ultimo_motivo,self.Recibe_otro,self.Foto_dni,self.Cobrar,
                    self.Reprogramaciones,self.Columna1,self.Columna2)
        try:
            cursor.execute(sql,values)
            midb.commit()
            midb.close()
            return True
        except mysql.connector.errors.IntegrityError:
            return False

    def updateDB(self):
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = """update ViajesFlexs set `Check` = %s ,Zona = %s ,Fecha = %s ,nro_venta = %s ,comprador = %s ,Telefono = %s ,
            Direccion = %s ,Referencia = %s ,Localidad = %s ,capital = %s ,CP = %s ,Vendedor = %s ,Chofer = %s ,Observacion = %s ,Motivo = %s ,Direccion_Completa = %s ,Currentlocation = %s ,
            Timechangestamp = %s ,Latitud = %s ,Longitud = %s ,Precio_Cliente = %s ,Precio_Chofer = %s ,Scanner = %s ,estado_envio = %s ,Foto_domicilio = %s ,Firma_Entregado = %s ,
            tipo_envio = %s ,Correo_chofer = %s ,Ultimo_motivo = %s ,Recibe_otro = %s ,Foto_dni = %s ,Cobrar = %s ,Reprogramaciones = %s ,`Columna 1` = %s ,`Columna 2` = %s )
            where Numero_envío = %s"""
        values = (self.Check,self.Zona,self.Fecha,self.nro_venta,self.comprador,
                    self.Telefono,self.Direccion,self.Referencia,self.Localidad,self.capital,self.CP,
                    self.Vendedor,self.Chofer,self.Observacion,self.Motivo,self.Direccion_Completa,
                    self.Currentlocation,self.Timechangestamp,self.Latitud,self.Longitud,self.Precio_Cliente,
                    self.Precio_Chofer,self.Scanner,self.estado_envio,self.Foto_domicilio,self.Firma_Entregado,
                    self.tipo_envio,self.Correo_chofer,self.Ultimo_motivo,self.Recibe_otro,self.Foto_dni,self.Cobrar,
                    self.Reprogramaciones,self.Columna1,self.Columna2,self.Numero_envío)

    def distance_to(self,destino):
        return geodesic((self.Latitud,self.Longitud),(destino.Latitud,destino.Longitud)).kilometers

    def __str__(self):
        return f"{self.Direccion}, {self.Localidad}"