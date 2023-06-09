
conn = find_esp_ble()
conn.send(current_protocol)

if protocol needs more than 1 package:
    recieve till the last character
    save all  #send to database and all that stuff
else:
    recieve
    save all
process the final package