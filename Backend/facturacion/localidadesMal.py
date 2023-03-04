from flask import Blueprint, render_template, request, session,redirect
from Backend.auth import auth
from Backend.database import database

arregloLocalidades = Blueprint('arregloLocalidades', __name__, url_prefix='/')


@arregloLocalidades.route("/facturacion/arreglolocalidad",methods = ["GET","POST"])
@auth.login_required
def arregloLocalidad():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "GET":
        cabeceras = "H.id","H.Fecha","H.Numero_envío","H.Direccion_Completa","H.Localidad","V.CP","H.Precio","H.Costo","H.Vendedor","H.estado_envio","H.Chofer"
        sql = """
            select 
                H.id,H.Fecha,H.Numero_envío,H.Direccion_Completa,
                H.Localidad,V.CP,H.Precio,H.Costo,H.Vendedor,H.estado_envio,H.Chofer 
            from 
                historial_estados as H  join ViajesFlexs as V on H.Numero_envío = V.Numero_envío 
            where 
                ((H.Precio is null or H.Precio = 0) or (H.Costo is null or H.Costo = 0))
            and 
                (H.estado_envio in ("En Camino","Entregado") or H.motivo_noenvio like "%reprogramado%")
            and 
                not H.estado_envio = "Lista para Devolver"
            and
                H.Fecha >= "2023-01-01"
            and not H.Vendedor in ("MMS Logistica","MMS") 
            order by H.Fecha desc, H.Numero_envío"""
        cursor.execute(sql)
        resu = []
        cont = 0
        for x in cursor.fetchall():
            resu.append(x)
            cont += 1
        localidades = []
        cursor.execute("Select localidad from localidad")
        for x in cursor.fetchall():
            localidades.append(x[0])
        midb.close()
        return render_template("facturacion/arregloLocalidad.html", 
                                auth = session.get("user_auth"),
                                cabeceras = cabeceras,
                                mensaje_error = cont,
                                localidades = localidades,
                                viajes=resu)
    else:
        for x in request.form.keys():
            if "localidad" in x or "nEnvio" in x:
                continue
            localidad = request.form[x+"localidad"]
            nEnvio = request.form[x+"nEnvio"]
            if localidad == "":
                continue
            print(f"{x} -- > {localidad}")
            sql = """
            update 
                ViajesFlexs as V inner join historial_estados as H 
                    on V.Numero_envío = H.Numero_envío 
            set 
                V.Localidad = %s, H.Localidad = %s,
                H.Precio = precio(H.Vendedor,%s,V.columna_1),
                H.Costo = cotizarChofer(%s,V.tipo_envio,V.columna_1)
            where V.Numero_envío = %s and H.id = %s
            """
            # id = request.form.get("idReporte")
            # loc = request.form.get("localidad")
            # nEnvio = request.form.get("numeroEnvio")
            values = (localidad,localidad,localidad,localidad,nEnvio,x)
            print(values)
            cursor.execute(sql,values)
            midb.commit()
        midb.close()
        return redirect("/facturacion/arreglolocalidad")