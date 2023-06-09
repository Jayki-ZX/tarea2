# Definir los UUIDs de los servicios y características del dispositivo BLE
# DEVICE_ADDRESS = 'C0:49:EF:08:CC:56'
# SERVICE_UUID = '000000ff-0000-1000-8000-00805f9b34fb'
# CHARACTERISTIC_UUID = '0000ff01-0000-1000-8000-00805f9b34fb'

from gattlib import DiscoveryService, GATTRequester

# Discover esp
service = DiscoveryService("hci0")
devices = service.discover(2)
mac = ''

print("Found devices:")
for address, name in devices.items():
    print("name: {}, address: {}".format(name, address))
    if name == "ESP_GATTS_DEMO":
        print("Found esp32, saving mac address...")
        mac = address
        break

# Send protocol
req = GATTRequester(mac)

print("Sending protocol number...")
# el handle lo saque del prompt de la esp, en decimal es 42
req.write_by_handle(0x2A, "hola")

# Receive and process data
print("Waiting for data response...")

