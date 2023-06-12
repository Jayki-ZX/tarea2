import sqlite3 as sql

# Funcion que elimina las tablas creadas
def drop_tables():
    conn = sql.connect("tarea2.sqlite")
    cur = conn.cursor()
    cur.execute("DROP TABLE datosBLE")
    cur.execute("DROP TABLE logsBLE")
    cur.execute("DROP TABLE configBLE")
    cur.execute("DROP TABLE lossBLE")
    conn.commit()
    conn.close()

drop_tables()

create_table_datosBLE = '''CREATE TABLE datosBLE (
    data STRING,
    id_device STRING,
    mac STRING,
    timestamp STRING
);'''

create_table_logsBLE = '''CREATE TABLE logsBLE (
    id_device STRING,
    id_protocol INTEGER,
    mac STRING,
    timestamp STRING
);'''

create_table_configBLE = '''CREATE TABLE configBLE (
   id_protocol INTEGER
);'''

create_table_lossBLE = '''CREATE TABLE lossBLE (
    attemps INTEGER,
    connection_delay STRING  
);'''

conn = sql.connect("tarea2.sqlite")
cur = conn.cursor()
try:
    r1 = cur.execute(create_table_datosBLE)
    r2 = cur.execute(create_table_logsBLE)
    r3 = cur.execute(create_table_configBLE)
    r4 = cur.execute(create_table_lossBLE)
except Exception:
    pass

# Se configura el envio de mensajes variando los protocolos. Esto es un ejemplo para demostrar el correcto funcionamiento
cur.execute('''INSERT INTO configBLE values(0), (1), (2), (3), (0), (1), (2), (3)''')
print(cur.execute("SELECT * FROM configBLE").fetchall()) #Asi obtenemos el valor 1 de la entrada 1-esima
conn.commit()
conn.close()


# inicializa la BDD