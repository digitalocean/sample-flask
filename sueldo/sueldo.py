from database import connect_db
midb = connect_db()
cursor = midb.cursor()
cursor.execute("select Chofer,estado_envio,motivo_noenvio,Costo from historial_estados where not estado_envio in ('Retirado','No Vino','Listo para salir (Sectorizado)','En Camino')")
for x in cursor.fetchall():
    print(x)
