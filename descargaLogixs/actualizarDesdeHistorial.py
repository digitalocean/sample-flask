from database import database
def actualizarEstados(midatabase):
    dicNrosEnviosDB = {}
    cursor = midatabase.cursor()
    cursor.execute("select Numero_envío,estado_envio from ViajesFlexs")
    for x in cursor.fetchall():
        dicNrosEnviosDB[str(x[0])]=str(x[1])
    enviosHistorial = {}
    midatabase = database.verificar_conexion(midatabase)
    cursor = midatabase.cursor(buffered=True)
    cursor.execute("select * from historial_estados")
    for x in cursor.fetchall():
        if "flex a base" in str(x[4]).lower() or str(x[1]) == "None":
            continue 
        if x[1] in enviosHistorial.keys():
            enviosHistorial[str(x[1])].append(x[11])
        else:
            enviosHistorial[x[1]] = [x[11]]
    midatabase = database.verificar_conexion(midatabase)
    cursor.execute("select Numero_envío from ViajesFlexs where estado_envio != 'Entregado' or Motivo != 'Cancelado';")
    #Por cada numero de envio en ViajesFlexs que no este Entregados o cancelados:
    nEnviosActualizar = {}
    for x in cursor.fetchall():
        nro_envio = str(x[0])
        #Si el numero de envio tiene historial:
        if nro_envio in enviosHistorial.keys():
            historiales = enviosHistorial[nro_envio]
            estadoHistorial = historiales[-1]
            if nro_envio in dicNrosEnviosDB.keys():
                if dicNrosEnviosDB[nro_envio] == estadoHistorial:
                    continue
                if not estadoHistorial in nEnviosActualizar.keys():
                    nEnviosActualizar[estadoHistorial] = [str(nro_envio)]
                else:
                    nEnviosActualizar[estadoHistorial].append(str(nro_envio))
            print(f"{nro_envio} actualiza a {estadoHistorial}")        
    for x in nEnviosActualizar.keys():
        if len(nEnviosActualizar[x]) < 2:
            enviosTmp = "('"+str(nEnviosActualizar[x][0])+"')"
        else: 
            enviosTmp = tuple(nEnviosActualizar[x])
        sql = f"UPDATE ViajesFlexs SET estado_envio = '{x}' WHERE Numero_envío in {enviosTmp};"
        print(sql)
        cursor.execute(sql)
        midatabase.commit()