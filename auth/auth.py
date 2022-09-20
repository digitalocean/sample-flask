#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

import functools

from flask import (
    Blueprint, g, redirect, render_template, request, session, url_for
)
from database import database

auth = Blueprint('auth', __name__, url_prefix='/')

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("select nickname, tipoUsuario from usuario where nickname = %s", (user_id,))
        usuario = cursor.fetchone()
        g.user = usuario[0]
        g.auth = usuario[1]
        midb.close()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return render_template("login.html",titulo="Login")
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user is None:
            if not str(g.auth) in ("Admin","Administrador"):
                print(g.auth)
                session.clear()
                return render_template("login.html",titulo="Login",mensaje="Debe ingresar con una cuenta del tipo administrador para realizar esa accion")
            return view(**kwargs)
        return render_template("login.html",titulo="Login")
    return wrapped_view


@auth.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")
        midb = database.connect_db()
        cursor = midb.cursor()
        try:
            sql = f"select nickname, password, tipoUsuario from usuario where nickname = '{user}'"
            cursor.execute(sql)
            resultado = cursor.fetchall()
            midb.close()
            for x in resultado:
                if x[1] == password:
                    session.clear()
                    session['user_id'] = x[0]
                    session['user_auth'] = x[2]
                    return redirect(url_for("bienvenido"))
                else:
                    return render_template("login.html",titulo="Login", mensaje=U"Usuario y/o contraseña incorrecto")
        except:
            midb.close()
            return render_template("login.html",titulo="Login", mensaje=U"Usuario y/o contraseña incorrecto")
        
        
        else:
            return render_template("login.html",titulo="Login", mensaje=U"Usuario y/o contraseña incorrecto")

    else:
        return render_template("login.html",titulo="Login", mensaje=U"Usuario y/o contraseña incorrecto")




@auth.route('/logout')
def logout():
    if "user_id" in session:
        session.pop("user_id")
    return render_template("login.html",titulo="Login")