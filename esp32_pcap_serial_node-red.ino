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
#include "PCAP.h"
#include <cstring>

//===== SETTINGS =====//
#define CHANNEL 1
#define BAUD_RATE 115200
#define CHANNEL_HOPPING true //if true it will scan on all channels
#define MAX_CHANNEL 11 //(only necessary if channelHopping is true)
#define HOP_INTERVAL 500 //in ms (only necessary if channelHopping is true)


//===== Run-Time variables =====//
PCAP pcap = PCAP();
int ch = CHANNEL;
unsigned long lastChannelChange = 0;
unsigned long lastpcaprun = 0;
unsigned long lastpcapwrite = 0;
int a = 0;

//===== FUNCTIONS =====//

/* will be executed on every packet the ESP32 gets while beeing in promiscuous mode */
void sniffer(void *buf, wifi_promiscuous_pkt_type_t type){
  wifi_promiscuous_pkt_t* pkt = (wifi_promiscuous_pkt_t*)buf;
  wifi_pkt_rx_ctrl_t ctrl = (wifi_pkt_rx_ctrl_t)pkt->rx_ctrl;
  
  uint32_t timestamp = now(); //current timestamp 
  uint32_t microseconds = (unsigned int)(micros() - millis() * 1000); //micro seconds offset (0 - 999)
  uint32_t orig_len = (unsigned int)ctrl.sig_len;
  
  pcap.newPacketSerial(timestamp, microseconds, orig_len, pkt->payload); //send packet via Serial  
  delay(600);
}

esp_err_t event_handler(void *ctx, system_event_t *event){ 
  if (event->event_id == SYSTEM_EVENT_STA_GOT_IP){
    //Serial.println("Our IP address is " IPSTR"\n", IP2STR(&event->event_info.got_ip.ip_info.ip));
    Serial.println("IP ASSIGNED");
  }
  if (event->event_id == SYSTEM_EVENT_STA_START){
    ESP_ERROR_CHECK(esp_wifi_connect());
    Serial.println("CONNECTED");
  }
  return ESP_OK; 
  }


//===== SETUP =====//
void setup() {

  /* start Serial */
  Serial.begin(BAUD_RATE);
  delay(2000);
  Serial.println();
  
  Serial.println("<<START>>");
  

  /* setup wifi */
  nvs_flash_init();
  tcpip_adapter_init();
  ESP_ERROR_CHECK( esp_event_loop_init(event_handler, NULL) );
  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  ESP_ERROR_CHECK( esp_wifi_init(&cfg) );
  ESP_ERROR_CHECK( esp_wifi_set_storage(WIFI_STORAGE_RAM) );
  ESP_ERROR_CHECK( esp_wifi_set_mode(WIFI_MODE_STA) );
  wifi_config_t sta_config = { };

  //Assign ssid & password strings
  strcpy((char*)sta_config.sta.ssid, "WiFi-B2B7");
  strcpy((char*)sta_config.sta.password, "44635237");
  sta_config.sta.bssid_set = false;
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta_config));  
  ESP_ERROR_CHECK( esp_wifi_start() );
  delay(2000);
  esp_wifi_set_promiscuous(true);
  pcap.startSerial();
  esp_wifi_set_promiscuous_rx_cb(sniffer);
  wifi_second_chan_t secondCh = (wifi_second_chan_t)NULL;
  esp_wifi_set_channel(ch,secondCh);
}

//===== LOOP =====//
void loop() {
 
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
