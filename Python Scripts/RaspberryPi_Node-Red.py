import sys
import os
import time
import serial
import scapy.all as scapy
import json
import subprocess
from multiprocessing import Process, Pool



# Enable libpcap in scapy
scapy.conf.use_pcap = True

#Function to write Esp32 PCAP data to .pcap file in decryption
def writingPCAP(filename):
    f = open(filename, "wb")
    while True:
        ch = ser.read()
        f.write(ch)
        #f.flush()
        
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    check = 0
    while check < 3:
        line = ser.readline()
        if b"<<START>>" in line:
            msg1 = {'payload':"sniffer startted"}
            node.send(msg1)
            check += 1
        if b"CONNECTED" in line:
            check += 1
            msg2 = {'payload':"WiFi Conncted"}
            node.send(msg2)
        if b"IP ASSIGNED" in line:
            check += 1
            msg3 = {'payload':"IP Assigned to Esp32"}
            node.send(msg3)
            
    # Getting Pcap data in to a tempory file        
    pcapfile = "/home/pi/pkt.pcap"
    ssid='WiFi-B2B7'
    psk='44635237'
    p = Process(target=writingPCAP, args=(pcapfile,))
    p.start()
    
    msg4 = {'payload':"Processing started"}
    node.send(msg4)
    
    
    time.sleep(10)
    
    # Reading the bytes written in to pcapfile and return them to stdout as hexdump
    with subprocess.Popen('tail -f -c +0 {}|tshark -i - -b packets:50 -w "/home/pi/packets/file.pcap" -o wlan.enable_decryption:TRUE -o "uat:80211_keys:\\"wpa-pwd\\",\\"{}:{}\\""'.format(pcapfile,psk,ssid), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process0:
            
            plist = os.listdir(path='/home/pi/packets/')
            index = 1
            while len(plist) == 0:
                plist = os.listdir(path='/home/pi/packets/')
                time.sleep(10)
            while len(plist) != 0:
                #Get the packets files names list
                plist = os.listdir(path='/home/pi/packets/')
                pfile = "file_00000"
                pfilename = ""
                if index < 10:
                    pfile = "file_0000{}".format(index)
                elif index < 100:
                    pfile = "file_000{}".format(index)
                elif index < 1000:
                    pfile = "file_00{}".format(index)
                elif index < 10000:
                    pfile = "file_0{}".format(index)
                elif index < 100000:
                    pfile = "file_{}".format(index)
                for fname in plist:
                    #Get the file name
                    if pfile in fname:
                        pfilename = "/home/pi/packets/{}".format(fname)
                try:
                    
                    for packet in scapy.PcapReader(pfilename):
                        try:
                            if packet.haslayer(scapy.Dot11WEP):
                                    packet[scapy.Dot11WEP].decrypt(key=None)
                                    
                            msg7 = {'payload':scapy.hexdump(packet,dump=True)}
                            node.send(msg7)
                            time.sleep(0.3)
                        except Exception as error:
                            msg8 = {'payload':"Error-2: {}".format(error)}
                            node.send(msg8)
                except Exception as err:
                    msg9 = {'payload':"Error-1: {}".format(err)}
                    node.send(msg9)
                os.remove(pfilename)
                index = index + 1
                time.sleep(20)
            msg5 = {'payload':process0.stdout.read()}
            node.send(msg5)
            msg6 = {'payload':process0.stderr.read()}
            node.send(msg6)    
                
         
        






