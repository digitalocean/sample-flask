from flask import Blueprint,render_template,redirect,request,session
from Backend.database.database import connect_db
from Backend.auth import auth

ToDo = Blueprint('ToDo', __name__, url_prefix='/')

@ToDo.route("/tareas",methods=["GET","POST"])
@auth.login_required
def Todo():
    midb = connect_db()
    cursor = midb.cursor()
    if request.method == "GET":
        cursor.execute("Select fecha, tarea, descripcion, solicita from tareas order by prioridad desc")
        resu = cursor.fetchall()
        columnas = [i[0] for i in cursor.description]
        listaTareas = []
        for x in resu:
            listaTareas.append(x)
        return render_template("tareas/tabla.html",
                                columnas = columnas,
                                lista = listaTareas,
                                auth = session.get("user_auth"))
    elif request.method == "POST":
        tarea = request.form.get("tarea")
        descripcion = request.form.get("descripcion")
        solicita = session.get("user_id")
        cursor.execute("insert into tareas (tarea,descripcion,solicita,prioridad) values(%s,%s,%s,0);",(tarea,descripcion,solicita))
        midb.commit()
        return redirect("/tareas")