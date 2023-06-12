# Definir los UUIDs de los servicios y características del dispositivo BLE
# DEVICE_ADDRESS = 'C0:49:EF:08:CC:56'
# SERVICE_UUID = '000000ff-0000-1000-8000-00805f9b34fb'
# CHARACTERISTIC_UUID = '0000ff01-0000-1000-8000-00805f9b34fb'

from gattlib import DiscoveryService, GATTRequester

from struct import pack, unpack
import traceback
import time
import sys
from DatabaseWork import *

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


# Discover esp
initial_time = time.time()
service = DiscoveryService("hci0")
devices = service.discover(2)
mac = ''

print("Dispositivos encontradoss:")
for address, name in devices.items():
    print("nombre: {}, address: {}".format(name, address))
    if name == "ESP_GATTS_DEMO":
        print("Se encontró esp32, guardando su mac address...")
        mac = address
        break

# Send protocol
print("Conectando con la esp")
req = GATTRequester(mac)
end_time = time.time()
print("Conexión establecida, guardando dato Loss")
guardarLossBLE(str(end_time - initial_time))
req.exchange_mtu(100)
req.set_mtu(100)
#Ciclo while de envio y recibo de mensajes
iteracion = 0
while(True):
    protocolo_actual = consultarconfigBLE(iteracion)[0][0]
    print("Protocolo numero {}".format(protocolo_actual))
    print("Enviando protocolo de configuracion...")

    # el handle lo saque del prompt de la esp, en decimal es 42
    req.write_by_handle(0x2A, bytes([protocolo_actual]))

    # Receive and process data
    print("Esperando respuesta...")
    # SUPONGAMOS QUE EL PAQUETE RECIBIDO SE GUARDA EN LA VARIABLE package, una cadena binaria
    package = req.read_by_handle(0x2a)[0] #cambiar esta linea por la que recibe el paquete de la esp
    print("Recibido correctamente el paquete, guardando log de comunicación")
    # Se considera la id device igual que la mac para este caso
    guardarLogsBLE(mac, protocolo_actual, mac, str(time.time()))
    # Extrae los datos del paquete guardandolos en diccionarios
    headerDict, dataDict = mainUnpackPackage(package)
    print("Desempaquetado correctamente el paquete")
    # Guarda los datos en la base de datos tabla datosBLE
    guardarDatosBLE(headerDict, dataDict)
    print("Guardado correctamente en la base de datos")
    iteracion = (iteracion + 1) % 4
    time.sleep(1)