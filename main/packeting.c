#include <sensors.c>
#include <math.h>
#include <stdlib.h>
#include "esp_system.h"
#include "esp_mac.h"
#include "esp_log.h"
#include <string.h>
#include "esp_timer.h"

//Empaquetamiento 
unsigned short lengmsg[6] = {6, 16, 20, 44};
unsigned short dataLength(char protocol){
    return lengmsg[ (unsigned int) protocol];
}

//Empaquetamiento del header
//transport layer 0 es tcp y 1 es udp
char* header(char protocol, char transportLayer){
	char* head = malloc(12);
    int id_device = 10;
    memcpy((void*) head, (void*) &id_device, 2);
    uint8_t* MACaddrs = malloc(6);
	esp_efuse_mac_get_default(MACaddrs);
    memcpy((void*) &(head[2]), (void*) MACaddrs, 6);
	free(MACaddrs);
    head[8]= transportLayer;
	head[9]= protocol;
	unsigned short dataLen = dataLength(protocol);
	memcpy((void*) &(head[10]), (void*) &dataLen, 2);
	return head;
}

//Empaquetamiento del mensaje

// Funcion auxiliar para obtener el timestamp en milisegundos
uint32_t get_timestamp() {
    uint64_t timestamp = esp_timer_get_time();
    uint32_t timestamp_ms = round(timestamp / 1000.0);
    return timestamp_ms;
}
// Arma un paquete para el protocolo 0
// 18 12hdr 6data
char* dataprotocol0(){
    ESP_LOGI("breakpoint", "filling with data0");
    char* msg = malloc(dataLength(0)); //6
    msg[0] = 1;
    char batt = batt_sensor();
    msg[1] = batt;
    int t = 0; //Este es el timestamp
    memcpy((void*) &(msg[1]), (void*) &t, 4);
    return msg;
}

// Arma un paquete segun el protocolo 1
char* dataprotocol1(){
    ESP_LOGI("breakpoint", "filling with data1");
    char* msg = malloc(dataLength(1)); //16
    //1 byte
    msg [0] = 1;
    //1 byte
    float batt = batt_sensor();
    msg[1] = batt;
    //4 bytes
    int t = 0;
    memcpy((void*) &(msg[2]), (void*) &t, 4);
    //1 byte
    char temp = THPC_sensor_temp();
    msg[6] = temp;
    //4 bytes
    float press = THPC_sensor_pres();
    memcpy((void*) &(msg[7]), (void*) &press, 4);
    //1 byte
    char hum = THPC_sensor_hum();
    msg[11] = hum;
    //4 bytes
    float co = THPC_sensor_co();
    memcpy((void*) &(msg[12]), (void*) &co, 4);
    return msg;
}

// Arma un paquete segun el protocolo 2
char* dataprotocol2(){
    ESP_LOGI("breakpoint", "filling with data2");
    char* msg = malloc(dataLength(2)); //16
    //1 byte
    msg [0] = 1;
    //1 byte
    float batt = batt_sensor();
    msg[1] = batt;
    //4 bytes
    int t = 0;
    memcpy((void*) &(msg[2]), (void*) &t, 4);
    //1 byte
    char temp = THPC_sensor_temp();
    msg[6] = temp;
    //4 bytes
    float press = THPC_sensor_pres();
    memcpy((void*) &(msg[7]), (void*) &press, 4);
    //1 byte
    char hum = THPC_sensor_hum();
    msg[11] = hum;
    //4 bytes
    float co = THPC_sensor_co();
    memcpy((void*) &(msg[12]), (void*) &co, 4);
    //4 bytes
    float rms = Accelerometer_kpi_RMS();
    memcpy((void*) &(msg[16]), (void*) &rms, 4);
    return msg;
}

// Arma un paquete segun el protocolo 3
char* dataprotocol3(){
    ESP_LOGI("breakpoint", "filling with data3");
    char* msg = malloc(dataLength(3)); //16
    //1 byte
    msg [0] = 1;
    //1 byte
    float batt = batt_sensor();
    msg[1] = batt;
    //4 bytes
    int t = 0;
    memcpy((void*) &(msg[2]), (void*) &t, 4);
    //1 byte
    char temp = THPC_sensor_temp();
    msg[6] = temp;
    //4 bytes
    float press = THPC_sensor_pres();
    memcpy((void*) &(msg[7]), (void*) &press, 4);
    //1 byte
    char hum = THPC_sensor_hum();
    msg[11] = hum;
    //4 bytes
    float co = THPC_sensor_co();
    memcpy((void*) &(msg[12]), (void*) &co, 4);
    //4 bytes
    float rms = Accelerometer_kpi_RMS();
    memcpy((void*) &(msg[16]), (void*) &rms, 4);
    //4 bytes
    float ampx = Accelerometer_kpi_amp_x();
    memcpy((void*) &(msg[20]), (void*) &ampx, 4);
    //4 bytes
    float frecx = Accelerometer_kpi_frec_x();
    memcpy((void*) &(msg[20]), (void*) &frecx, 4);
    //4 bytes
    float ampy = Accelerometer_kpi_amp_y();
    memcpy((void*) &(msg[20]), (void*) &ampy, 4);
    //4 bytes
    float frecy = Accelerometer_kpi_frec_y();
    memcpy((void*) &(msg[20]), (void*) &frecy, 4);
    //4 bytes
    float ampz = Accelerometer_kpi_amp_z();
    memcpy((void*) &(msg[20]), (void*) &ampz, 4);
    //4 bytes
    float frecz = Accelerometer_kpi_frec_z();
    memcpy((void*) &(msg[20]), (void*) &frecz, 4);
    return msg;
}

unsigned short messageLength(char protocol){
    int headerLength = 12;
    return headerLength+dataLength(protocol);
}

//Empaqueta mensaje
char* mensaje (char protocol, char transportLayer){
	char* mnsj = malloc(messageLength(protocol));
	//mnsj[messageLength(protocol)-1]= '\0';
	char* hdr = header(protocol, transportLayer);
	char* data;
	switch (protocol) {
		case 0:
			data = dataprotocol0();
			break;
		case 1:
			data = dataprotocol1();
			break;
		case 2:
			data = dataprotocol2();
			break;
        case 3:
			data = dataprotocol3();
			break;
        default:
            data = dataprotocol0();
            break;
	}
	memcpy((void*) mnsj, (void*) hdr, 12);
	memcpy((void*) &(mnsj[12]), (void*) data, dataLength(protocol));
	free(hdr);
	free(data);
	return mnsj;
}