import mysql.connector

def connect_db():
    midb = mysql.connector.connect(
    host="141.136.39.86",
    user="mmslogis_GS",
    password="12345",
    database="mmslogis_MMSPack"
    )
    return midb

def verificar_conexion(midb):
    if midb.is_connected() == False:
        print("Reconectando base de datos")
    while midb.is_connected() == False:
        try:
            midb = connect_db()
            conexion = midb.is_connected()
            print("Conexion exitosa")
        except:
            print("Error en la coneccion")
    return midb


from flask import Flask
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="abcd1234"
)



@app.route("/")
def bienvenido():
    return "Hola Mundo"

@app.route("/api/users/create",methods=["POST","GET"])
def test():
    data = request.get_json()
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(f"insert into empleado (nombre,puesto,vehiculo,patente,correo,dni,cbu,telefono,direccion,localidad,password) values('{data['nombre']}','{data['puesto']}','{data['vehiculo']}','{data['patente']}','{data['correo']}','{data['dni']}','{data['cbu']}','{data['telefono']}','{data['direccion']}','{data['localidad']}','{data['password']}')")
    midb.commit()
    midb.close()
    return "algo"


@app.route("/api/users/login",methods=["POST","GET"])
def loginAppMovil():
    dataLogin = request.get_json()
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select id,nombre,password from empleado where dni = {dataLogin['dni']}")
    res = cursor.fetchone()
    midb.close()
    if dataLogin["password"] == res[2]:
        print("True")
        return "{success:True,message:'usuario validado',data:""'}"
    else:
        return "Contraseña incorrecta"
