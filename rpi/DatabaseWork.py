import json
import sqlite3 as sql

# Funcion que guarda los datos recibidos por BLE en la tabla datosBLE
def consultarTabla(tabla):
    with sql.connect("tarea2.sqlite") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM {}".format(tabla))
        return cur.fetchall()

def guardarLogsBLE(id_device, id_protocol, mac, timestamp):
    with sql.connect("tarea2.sqlite") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO logsBLE (id_device, id_protocol, mac, timestamp) VALUES (?, ?, ?, ?)", (id_device, id_protocol, mac, timestamp))

        conn.commit()

def guardarLossBLE(time):
    with sql.connect("tarea2.sqlite") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO lossBLE (attemps, connection_delay) VALUES (1, {})".format(time))
        conn.commit()

def guardarDatosBLE(headerDict, dataDict):
    with sql.connect("tarea2.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO datosBLE (data, id_device, mac, timestamp) VALUES (?, ?, ?, ?)", (json.dumps(dataDict), headerDict["id_device"], headerDict["mac"], dataDict["timestamp"]))
        conn.commit()

# Funcion que obtiene la configuracion i-esima a enviar a esp
def consultarconfigBLE(i):
    with sql.connect("tarea2.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM configBLE LIMIT 1 OFFSET {i}")
        return cur.fetchall()

