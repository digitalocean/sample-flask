from flask import Blueprint,redirect,session
from auth import auth
from geopy.distance import geodesic
from .Reparto import Reparto
from .Destino import Destino
from database import database

lgMR = Blueprint('RutaChofer', __name__, url_prefix='/')

def asignarCercano(reparto,parada):
    menorDistancia = None
    for i,dest in enumerate(reparto.destinos):    
        distancia = geodesic((parada.latitud,parada.longitud),(dest.latitud,dest.longitud)).kilometers
        if parada.envio == dest.envio:
            continue
        if menorDistancia == None:
            menorDistancia = distancia
            parada.cercano = dest
            parada.distanciaCercano = menorDistancia
        elif distancia < parada.distanciaCercano:
            parada.cercano = dest
            parada.distanciaCercano = distancia
    reparto.eliminarDestino(parada)
    if parada.cercano != None:
        asignarCercano(reparto,parada.cercano)


def crearRuta(destino,stringRuta,contador):
    if contador < 25:
        stringRuta += f"{destino.direccionCompleta}/"
    if destino.cercano != None:
        stringRuta = crearRuta(destino.cercano,stringRuta,contador+1)
    return stringRuta



@lgMR.route("/miruta")
@auth.login_required
def miRuta():
    repartoChofer = Reparto()
    midb = database.connect_db()
    cursor = midb.cursor()
    chofer = session.get("user_id")
    cursor.execute(f"select Numero_envío,latitud,longitud,Direccion,Localidad from ViajesFlexs where Chofer = '{chofer}' and estado_envio in ('En Camino','Reasignado')")
    resultado = cursor.fetchall()
    midb.close()
    origen = Destino("0","-34.608609", "-58.419144","av. Diaz Velez 3750", "Almagro")
    repartoChofer.agregarDestino(origen)
    for x in resultado:
        destino = Destino(x[0],x[1],x[2],x[3],x[4])
        repartoChofer.agregarDestino(destino)
    asignarCercano(repartoChofer,origen)
    return redirect("https://www.google.com/maps/dir/" + crearRuta(origen,"",0))



@lgMR.route("/turuta/<chofer>")
def tuRuta(chofer):
    repartoChofer = Reparto()
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select Numero_envío,latitud,longitud,Direccion,Localidad from ViajesFlexs where Chofer = '{chofer}' and estado_envio in ('En Camino','Reasignado')")
    resultado = cursor.fetchall()
    midb.close()
    origen = Destino("0","-34.608609", "-58.419144","av. Diaz Velez 3750", "Almagro")
    repartoChofer.agregarDestino(origen)
    for x in resultado:
        destino = Destino(x[0],x[1],x[2],x[3],x[4])
        repartoChofer.agregarDestino(destino)
    asignarCercano(repartoChofer,origen)
    return redirect("https://www.google.com/maps/dir/" + crearRuta(origen,"",0))