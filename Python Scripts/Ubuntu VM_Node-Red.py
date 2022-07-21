#! /usr/bin/env python3

import time
import sys
import subprocess
import scapy.all as scapy
import re

scapy.conf.use_pcap = True

#msg0 = {'payload': sys.version}
#node.send(msg0)
hexdump_pkt = msg['payload']

packet = scapy.Dot11(scapy.import_hexcap(input_string=hexdump_pkt))

#td_packet = str(scapy.tcpdump(packet, dump=True))
msg1 = {'payload':packet.show2(dump=True)}
#msg1 = {'payload':td_packet}
msg2 = {'payload':packet.sprintf(" Packet Type = %Dot11.type%\n Packet Subtype = %Dot11.subtype%\n Protocol Version = %Dot11.proto%\n cfe = %Dot11.cfe%\n FCField = %Dot11.FCfield%\n ID = %Dot11.ID%\n addr1 = %Dot11.addr1%\n addr2 = %Dot11.addr2%\n addr3 = %Dot11.addr3%\n SC = %Dot11.SC%\n addr4 = %Dot11.addr4%")}


#filtering the packets for wifi SSID which ESP32 connected to
ssid = "WiFi-B2B7"
psk = "44635237"

#Filtering management packets with infomation element 
msg3 = {'payload':"None"}
if packet.haslayer(scapy.Dot11Elt):
    for layer in packet.iterpayloads():
        
        if type(layer) == scapy.Dot11Elt:
        
            if layer.fields['ID'] == 0:
                if 'info' in layer.fields:
                    if ssid in str(layer.fields['info']):
                    
                        msg3['payload'] = packet.show2(dump=True)
                    
#Filtering data packets
msg4 = {'payload':"none"}
msg5 = {'payload':"null"}
msg6 = {'payload':"Null"}
if packet.sprintf("%Dot11.type%") == "Data":
   if (packet.sprintf("%Dot11.subtype%") != "Null (no data)") and (packet.sprintf("%Dot11.subtype%") != "QoS Null (no data)"):
        msg4['payload']  = scapy.hexdump(packet,dump=True)
        msg5['payload'] = packet.show2(dump=True)
        
        # Searching for hexdump data packets with RE of user,pass and http
        pattern1 = re.compile(r'http',re.I|re.A)
        pattern2 = re.compile(r'(user|pass)',re.I|re.A)
        match1 = pattern1.search(msg4['payload'])
        if match1 != None:
            match2 = pattern2.search(msg4['payload'])
            if match2 != None:
                msg6['payload'] = msg4['payload']
        
        
        
return [msg1, msg2, msg3, msg4, msg5, msg6]
