import mysql.connector
midb = mysql.connector.connect(
            host = "109.106.251.113",
            user="mmslogis_GS",
            password="12345",
            database="mmslogis_MMSPack"
            )
dic = {"111122333","41848503917"}
tup = tuple(dic)
print(tup)

cursor = midb.cursor()
cursor.execute(f"select * from ViajesFlexs where Numero_envío in {tup}")
for x in cursor.fetchall():
    print(x)