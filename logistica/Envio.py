from flask import session
from datetime import datetime,timedelta
from geopy.distance import geodesic
from database import database
import mysql.connector
from .script import geocoder
class Envio:
    def __init__(self,direccion,localidad,vendedor,numeroEnvio=None,comprador=None,telefono=None,referencia=None,cp=None,fecha=datetime.now(),numeroVenta=None,chofer=None,observacion=None,
                motivo=None,precio=None,costo=None,scanner=None,estadoEnvio="Lista Para Retirar",fotoDomicilio=None,firma=None,tipoEnvio=2,latitud=None,longitud=None,correoChofer=None,
                recibeOtro=None,fotoDni=None,cobrar=0,reprogramaciones=0,valorDeclarado=None,sku=None,multiplicador=1,columna2=None,columna3=None,fromDB=False,geolocalizar=False):
        midb = database.connect_db()
        if numeroEnvio == None:
            cursor = midb.cursor()
            cursor.execute("select count(*),idVendedor(%s) from ViajesFlexs",(vendedor,))
            res = cursor.fetchone()
            caracteres = len(f"{res[1]}{res[0]}{tipoEnvio}")
            agregar = 11 - caracteres
            self.Numero_envío = f"NOML{tipoEnvio}-{res[1]}{str(0)*agregar}{res[0]}"
        else:
            chars = '.,!"#$%&/()=?¡¿'
            self.Numero_envío = numeroEnvio.translate(str.maketrans('', '', chars))
        if type(numeroEnvio) != None and not fromDB:
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
        direccionCompleta = direccion + ", " + localidad + ", buenos aires"
        self.Check = None
        self.Zona = None
        self.Fecha = fecha
        self.nro_venta = numeroVenta
        self.comprador = comprador
        self.Telefono = telefono
        self.Direccion = direccion
        self.Referencia = referencia
        self.Localidad = localidad
        self.Latitud = latitud
        self.Longitud = longitud
        self.rendido = None
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
        self.Recibe_otro = recibeOtro
        self.Foto_dni = fotoDni
        self.Cobrar = cobrar
        self.Reprogramaciones = reprogramaciones
        self.valordeclarado = valorDeclarado
        self.SKU = sku
        self.Multiplicador = multiplicador
        self.columna_2 = columna3
        self.columna_3 = columna3
    def toDB(self):
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = """insert into ViajesFlexs (`Check`,Zona,Fecha,Numero_envío,nro_venta,comprador,Telefono,
            Direccion,Referencia,Localidad,rendido,CP,Vendedor,Chofer,Observacion,Motivo,Direccion_Completa,Currentlocation,
            Timechangestamp,Latitud,Longitud,Precio_Cliente,Precio_Chofer,Scanner,estado_envio,Foto_domicilio,Firma_Entregado,
            tipo_envio,Correo_chofer,Recibe_otro,Foto_dni,Cobrar,Reprogramaciones,`valordeclarado`,`sku`,columna_1,columna_2,columna_3)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (self.Check,self.Zona,self.Fecha,self.Numero_envío,self.nro_venta,self.comprador,
                    self.Telefono,self.Direccion,self.Referencia,self.Localidad,self.rendido,self.CP,
                    self.Vendedor,self.Chofer,self.Observacion,self.Motivo,self.Direccion_Completa,
                    self.Currentlocation,self.Timechangestamp,self.Latitud,self.Longitud,self.Precio_Cliente,
                    self.Precio_Chofer,self.Scanner,self.estado_envio,self.Foto_domicilio,self.Firma_Entregado,
                    self.tipo_envio,self.Correo_chofer,self.Recibe_otro,self.Foto_dni,self.Cobrar,
                    self.Reprogramaciones,self.valordeclarado,self.SKU,self.Multiplicador,self.columna_2,self.columna_3)
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
        cursor.execute("""select `Check`,Zona,Fecha,nro_venta,comprador,Telefono,Direccion,Referencia,Localidad,rendido,
                        CP,Vendedor,Chofer,Observacion,Motivo,Direccion_Completa,Currentlocation,Timechangestamp,Latitud,Longitud,
                        Precio_Cliente,Precio_Chofer,Scanner,estado_envio,Foto_domicilio,Firma_Entregado,tipo_envio,Correo_chofer,columna_1,Recibe_otro,
                        Foto_dni,Cobrar,Reprogramaciones,`valordeclarado`,`sku`,Numero_envío
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
            Check = "En Camino"
            Zona = null
        "Entregado":
            motivo = "Entregado sin novedades"
        "No visitado":
            estado = "No Entregado"
            motivo = "Domicilio no visitado"
        "reprogramado":
            estado = "No Entregado"
            motivo = "Nadie en Domicilio (Reprogramado)
        "zonaPeligrosa":
            estado = "No Entregado"
            motivo = "Zona Peligrosa"
        "fueraDeZona":
            estado = "Fuera de Zona"
            motivo = "Fuera de Zona"
            """
        midb = database.connect_db()
        cursor = midb.cursor()
        numEnvio=self.Numero_envío
        modifica=session.get("user_id")
        motivo = None
        check = None
        hora = datetime.now()-timedelta(hours=3)
        if estado == "En Camino":
            check = "En Camino"
        elif estado == "Entregado":
            motivo = "Entregado sin novedades"
        elif estado == "No visitado":
            estado = "No Entregado"
            motivo = "Domicilio no visitado"
        elif estado == "reprogramado":
            estado = "No Entregado"
            motivo = "Nadie en Domicilio (Reprogramado)"
        elif estado == "zonaPeligrosa":
            estado = "No Entregado"
            motivo = "Zona Peligrosa"
        elif estado == "fueraDeZona":
            estado = "Fuera de Zona"
            motivo = "Fuera de Zona"
        sql = "update ViajesFlexs set Zona = null, `Check` = %s, estado_envio = %s, Motivo = %s,Chofer = %s,Correo_chofer=correoChofer(%s),Foto_domicilio = concat('Modifico: ',%s),Timechangestamp=%s where Numero_envío = %s"
        values = (check,estado,motivo,chofer,chofer,modifica,hora,numEnvio)
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