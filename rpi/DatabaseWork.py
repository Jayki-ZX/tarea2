import json
import sqlite3 as sql

# Funcion que guarda los datos recibidos por BLE en la tabla datosBLE
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

