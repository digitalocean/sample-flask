from flask import session
from datetime import datetime,timedelta
from geopy.distance import geodesic
from database import database
import mysql.connector
class Envio:
    def __init__(self,direccion,localidad,vendedor,numeroEnvio=None,comprador=None,telefono=None,referencia=None,cp=None,fecha=datetime.now(),numeroVenta=None,chofer=None,observacion=None,
                motivo=None,precio=None,costo=None,scanner=None,estadoEnvio="Lista Para Retirar",fotoDomicilio=None,firma=None,tipoEnvio=2,latitud=None,longitud=None,correoChofer=None,
                recibeOtro=None,fotoDni=None,cobrar=0,reprogramaciones=0,valorDeclarado=None,sku=None,multiplicador=1,columna2=None,columna3=None,fromDB=False,geolocalizar=False,zona=None):
        midb = database.connect_db()
        if numeroEnvio == None:
            cursor = midb.cursor()
            cursor.execute("select count(*),idVendedor(%s) from ViajesFlexs",(vendedor,))
            res = cursor.fetchone()
            caracteres = len(f"{res[1]}{res[0]}{tipoEnvio}")
            agregar = 11 - caracteres
            self.Numero_envío = f"NOML{tipoEnvio}{res[1]}{str(0)*agregar}{res[0]}"
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
        self.Zona = zona
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

    def enCamino(self,chofer,fechaHora=str(datetime.now()-timedelta(hours=3))[0:-7]):
        midb = database.connect_db()
        cursor = midb.cursor()
        modifica=session.get("user_id")
        sql = """
        INSERT INTO `mmslogis_MMSPack`.`en_camino`
            (`id`,
            `fecha`,
            `hora`,
            `Numero_envío`,
            `chofer`,
            `scanner`)
            VALUES
            (UUID(),
            %s,
            %s,
            %s,
            correoChofer(%s),
            "Asignado por %s");"""
        cursor.execute(sql,(fechaHora,fechaHora,self.Numero_envío,chofer,modifica))
        midb.commit()

    def entregado(self,chofer,fechaHora=str(datetime.now()-timedelta(hours=3))[0:-7]):
        midb = database.connect_db()
        cursor = midb.cursor()
        modifica=session.get("user_id")
        sql = """update ViajesFlexs set 
                    Zona = null, 
                    `Check` = null, 
                    estado_envio = 'Entregado', 
                    Motivo = 'Entregado sin novedades',
                    Chofer = %s,
                    Correo_chofer=correoChofer(%s),
                    Foto_domicilio = concat('Modifico: ',%s),
                    Timechangestamp=%s 
                    where Numero_envío = %s"""
        cursor.execute(sql,(chofer,chofer,modifica,fechaHora,self.Numero_envío))
        midb.commit()


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