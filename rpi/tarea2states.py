from gattlib import DiscoveryService, GATTRequester

from struct import pack, unpack
import traceback
import time
import sys
from DatabaseWork import *
# Definir los UUIDs de los servicios y características del dispositivo BLE

# Funciones de desempaquetamiento
# Patron de desempaquetamiento de la data
def dataUnpack(protocol:int, data):
    protocol_unpack = ["<BBl", "<BBlBfBf", "<BBlBfBff", "<BBlBfBffffffff"]
    return unpack(protocol_unpack[protocol], data)

# Patron de desempaquetamiento del header
def headerUnpack(header):
    return unpack("<h6BBBH", header)

# Desempaquetamiento de la data
def mainUnpackData(protocol:int, data):
    if protocol not in [0, 1, 2, 3]:
        print("Error: protocol doesnt exist")
        return None
    def protFunc(protocol, keys):
        def p(data):
            unp = dataUnpack(protocol, data)
            return {key:val for (key,val) in zip(keys, unp)}
        return p
    p0 = ["Val", "Batt_level", "timestamp"]
    p1 = ["Val", "Batt_level", "timestamp", "Temp", "Pres", "Hum", "Co"]
    p2 = ["Val", "Batt_level", "timestamp", "Temp", "Pres", "Hum", "Co", "RMS"]
    p3 = ["Val", "Batt_level", "timestamp", "Temp", "Pres", "Hum", "Co", "RMS", "Ampx", "Frecx", "Ampy", "Frecy", "Ampz", "Frecz"]
    p = [p0, p1, p2, p3]

    try:
        return protFunc(protocol, p[protocol])(data)
    except Exception:
        print("Data unpacking Error:", traceback.format_exc())
        return None

# Desempaquetamiento del header
def mainUnpackHeader(header):
    id_device, M1, M2, M3, M4, M5, M6, transport_layer, protocol, leng_msg = headerUnpack(header)
    MAC = ".".join([hex(x)[2:] for x in [M1, M2, M3, M4, M5, M6]])
    return {"id_device": id_device, "mac":MAC, "protocol":protocol, "transport_layer":transport_layer, "length":leng_msg}

# Desempaquetamiento del paquete completo (header + data)
def mainUnpackPackage(package):
    header = package[0:12]
    data = package[12:]
    headerDict = mainUnpackHeader(header)
    dataDict = mainUnpackData(headerDict["protocol"], data)
    return headerDict, dataDict

#Perdida de paquetes
lengmsg = [6, 16, 20, 44]
def dataLength(protocol):
    return lengmsg[protocol]

# Dado un protocolo, retorna el largo esperado del mensaje
def messageLength(protocol):
    return 12+dataLength(protocol)

#Funcion que calcula la perdida de paquetes. Recibe la data de la esp y el protocolo al que corresponde
def perdida(data, protocol):
    messageLength(protocol) - sys.getsizeof(data)

# Definir los estados de la máquina de estado
STATE_DISCONNECTED = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2

# Inicializar la conexión PyGatt y el estado inicial de la máquina de estado
req = -1
mac = ''
iteracion = 0
protocol = consultarconfigBLE(iteracion)[0][0]

state = STATE_DISCONNECTED

# Función para manejar eventos de conexión
def handle_connection_event(event):
    global state
    if event == 'disconnected':
        print('El dispositivo se desconectó')
        state = STATE_DISCONNECTED
    elif event == 'connected':
        print('El dispositivo se conectó')
        state = STATE_CONNECTED

# Función para conectar al dispositivo BLE
def connect():
    global state
    global req
    global mac
    state = STATE_CONNECTING
    initial_time = time.time()

    # encontrar la esp por discovery en la primera conexion
    if mac == '':
        service = DiscoveryService("hci0")
        devices = service.discover(2)
        print("Dispositivos encontradoss:")
        for address, name in devices.items():
            print("nombre: {}, address: {}".format(name, address))
            if name == "ESP_GATTS_DEMO":
                print("Se encontró esp32, guardando su mac address...")
                mac = address
                break
    
    print("Conectando con la esp")
    print(mac)
    req = GATTRequester(mac)
    end_time = time.time()
    print("Conexión establecida, guardando dato Loss")
    guardarLossBLE(str(end_time - initial_time))

    # fuera del estandar
    req.exchange_mtu(100)
    req.set_mtu(100)
    


# Función para desconectar del dispositivo BLE
def disconnect():
    global state
    global req
    state = STATE_DISCONNECTED
    req.disconnect()

# Función para manejar notificaciones de características
def handle_notification(handle, value):
    print('Notificación recibida:', value.hex())

def send_protocol():
    global state
    ans = req.write_by_handle(0x2A, bytes([protocol]))
    if ans[0] == b'\x13':
        print("Se envió correctamente protocolo de configuracion...")
        # se recibio el OK de la esp, por lo que se puede leer el mensaje
        state = STATE_CONNECTED

# leer 1 vez y pasar al siguiente protocolo
def read_msg():
    global protocol
    global iteracion
    print("Esperando respuesta...")
    msg = req.read_by_handle(0x2A)[0]
    print("Recibido correctamente el paquete, guardando log de comunicación")
    # Se considera la id device igual que la mac para este caso
    guardarLogsBLE(mac, protocol, mac, str(time.time()))
    # Extrae los datos del paquete guardandolos en diccionarios
    headerDict, dataDict = mainUnpackPackage(msg)
    print("Desempaquetado correctamente el paquete")
    # Guarda los datos en la base de datos tabla datosBLE
    guardarDatosBLE(headerDict, dataDict)
    print("Guardado correctamente en la base de datos")

    iteracion = (iteracion + 1) % 4
    protocol = consultarconfigBLE(iteracion)[0][0]
    print("Protocolo numero {}".format(protocol))
    disconnect()

# Bucle principal de la máquina de estado
tries = 0
while True:
    if state == STATE_DISCONNECTED:
        # Si el estado actual es desconectado, intentar conectar
        connect()
    elif state == STATE_CONNECTING:
        # Si el estado actual es conectando, esperar hasta que se conecte o se agote el tiempo de espera
        try:
            tries += 1
            send_protocol()
            time.sleep(1)
            if tries == 10:
                print("Couldn't connect after 10 tries, shutting down")
                disconnect()
        except Exception:
            print("Still not connected, trying again")
    elif state == STATE_CONNECTED:
        # Si el estado actual es conectado, hacer cualquier operación necesaria en el dispositivo
        read_msg()
