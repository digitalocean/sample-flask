from flask import Blueprint,render_template,redirect,request
from Backend.database.database import connect_db
ToDo = Blueprint('ToDo', __name__, url_prefix='/')

@ToDo.route("/tareas",methods=["GET","POST"])
def Todo():
    midb = connect_db()
    cursor = midb.cursor()
    if request.method == "GET":
        cursor.execute("Select * from tareas")
        resu = cursor.fetchall()
        columnas = [i[0] for i in cursor.description]
        listaTareas = []
        for x in resu:
            listaTareas.append(x)
        return render_template("tareas/tabla.html",
                                columnas = columnas,
                                lista = listaTareas)
    elif request.method == "POST":
        tarea = request.form.get("tarea")
        descripcion = request.form.get("descripcion")
        cursor.execute("insert into tareas (tarea,descripcion,solicita,prioridad) values(%s,%s,'alguien',0);",(tarea,descripcion))
        midb.commit()
        return redirect("/tareas")