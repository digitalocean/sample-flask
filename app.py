
from flask import Flask
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="abcd1234"
)
CORS(app)



@app.route("/")
@auth.login_required
def bienvenido():
    return "Hola Mundo"

from database import database
@app.route("/api/users/create",methods=["POST","GET"])
def test():
    data = request.get_json()
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"insert into empleado (nombre,puesto,vehiculo,patente,correo,dni,cbu,telefono,direccion,localidad,password) values('{data['nombre']}','{data['puesto']}','{data['vehiculo']}','{data['patente']}','{data['correo']}','{data['dni']}','{data['cbu']}','{data['telefono']}','{data['direccion']}','{data['localidad']}','{data['password']}')")
    midb.commit()
    midb.close()
    return "algo"


@app.route("/api/users/login",methods=["POST","GET"])
def loginAppMovil():
    dataLogin = request.get_json()
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select id,nombre,password from empleado where dni = {dataLogin['dni']}")
    res = cursor.fetchone()
    midb.close()
    if dataLogin["password"] == res[2]:
        print("True")
        return "{success:True,message:'usuario validado',data:""'}"
    else:
        return "Contraseña incorrecta"
