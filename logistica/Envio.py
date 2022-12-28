from flask import session
from datetime import datetime,timedelta
from geopy.distance import geodesic
from database import database
import mysql.connector
from .script import geocoder
class Envio:
    def __init__(self,direccion,localidad,vendedor,numeroEnvio=None,comprador=None,telefono=None,referencia=None,cp=None,fecha=datetime.now(),numeroVenta=None,chofer=None,observacion=None,
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
        if numeroEnvio == None:
            cursor = midb.cursor()
            cursor.execute("select count(*) from ViajesFlexs")
            res = cursor.fetchone()
            caracteres = len(str(res[0]))
            agregar = 10 - caracteres - len(str(tipoEnvio))
            self.Numero_envío = f"NOML{tipoEnvio}"+ "0"*agregar + str(res[0])
        else:
            chars = '.,!"#$%&/()=?¡¿'
            self.Numero_envío = numeroEnvio.translate(str.maketrans('', '', chars))
        direccionCompleta = direccion + ", " + localidad + ", buenos aires"
        if latitud == None or longitud == None:
            print("geolocaliza")
            latlong = geocoder(direccionCompleta)
            self.Latitud = latlong[0]
            self.Longitud = latlong[1]
            if fromDB:
                midb = database.connect_db()
                cursor = midb.cursor()
                cursor.execute(f"update ViajesFlexs set Latitud = '{latlong[0]}', Longitud = '{latlong[1]}' where Numero_envío = '{numeroEnvio}'")
                midb.commit()
                midb.close()
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
            return self.Numero_envío
        except mysql.connector.errors.IntegrityError:
            return False
    @classmethod
    def fromDB(self,nroEnvio):
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("""select `Check`,Zona,Fecha,nro_venta,comprador,Telefono,Direccion,Referencia,Localidad,capital,
                        CP,Vendedor,Chofer,Observacion,Motivo,Direccion_Completa,Currentlocation,Timechangestamp,Latitud,Longitud,
                        Precio_Cliente,Precio_Chofer,Scanner,estado_envio,Foto_domicilio,Firma_Entregado,tipo_envio,Correo_chofer,Ultimo_motivo,Recibe_otro,
                        Foto_dni,Cobrar,Reprogramaciones,`Columna 1`,`Columna 2`,Numero_envío
                        from ViajesFlexs where Numero_envío = %s""",(nroEnvio,))
        viaje = cursor.fetchone()
        if viaje != None:
            return Envio(viaje[6],viaje[8],viaje[11],viaje[35],viaje[4],viaje[5],viaje[7],viaje[10],viaje[2],viaje[3],
                        viaje[12],viaje[13],viaje[14],viaje[20],viaje[21],viaje[22],viaje[23],viaje[24],viaje[25],viaje[26],
                        viaje[18],viaje[19],viaje[28],viaje[29],viaje[19],viaje[30],viaje[31],viaje[32],viaje[33],viaje[34],True)
        else:
            return False
    def cambioEstado(self,estado,chofer):
        """
        "En Camino":
            motivo = "En Camino"
        
        "Entregado":
            motivo = "Entregado sin novedades"
        el
        "No visitado":
            estado = "No Entregado"
            motivo = "Domicilio no visitado"
        el
        "reprogramado":
            estado = "No Entregado"
            motivo = "Nadie en Domicilio (Reprogramado)"""
        midb = database.connect_db()
        cursor = midb.cursor()
        numEnvio=self.Numero_envío
        modifica=session.get("user_id")
        sql = "update ViajesFlexs set estado_envio = %s, Motivo = %s,Chofer = %s,Correo_chofer=correoChofer(%s),Foto_domicilio = concat('Modifico: ',%s),Timechangestamp=%s where Numero_envío = %s"
        motivo = None
        hora = datetime.now()-timedelta(hours=3)
        if estado == "En Camino":
            motivo = "En Camino"
        if estado == "Entregado":
            motivo = "Entregado sin novedades"
        elif estado == "No visitado":
            estado = "No Entregado"
            motivo = "Domicilio no visitado"
        elif estado == "reprogramado":
            estado = "No Entregado"
            motivo = "Nadie en Domicilio (Reprogramado)"
        values = (estado,motivo,chofer,chofer,modifica,hora,numEnvio)
        cursor.execute(sql,values)
        midb.commit()
        midb.close()
    @classmethod
    def deleteFromDB(self,nroEnvio):
        sql = "delete from ViajesFlexs where Numero_envío = %s"
        values =(nroEnvio,)
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute(sql,values)
        midb.commit()
        midb.close()    
    def distance_to(self,destino):
        return geodesic((self.Latitud,self.Longitud),(destino.Latitud,destino.Longitud)).kilometers

    def __str__(self):
        return f"{self.Direccion}, {self.Localidad}"