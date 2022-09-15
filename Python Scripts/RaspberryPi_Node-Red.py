import sys
import os, shutil
import time
import serial
import scapy.all as scapy
import pickle
import signal
import subprocess
from multiprocessing import Process, Pool
from gpiozero import DigitalOutputDevice as Dout
from datetime import datetime

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
    # Initializing GPIO 17 to later use of esp reboot
    espreboot = Dout(17)
    while True:    
        # Kill the previous stared project if still running
        try:
            with open('data.pickle', 'rb') as f:
                process_id = pickle.load(f)
                os.kill(process_id, signal.SIGTERM)
        except Exception as error0:
            msg10 = {'payload':"Error-0:{}".format(error0)}
            node.send(msg10)
            
        # Defining the serial port
        ser = serial.Serial()
        ser.baudrate = 115200
        ser.port = '/dev/ttyAMA0'
        if ser.is_open:
            ser.close()
        ser.open()
        
        # Seting GPIO 17 to HIGH to reboot the Esp32
        espreboot.on()
        
        # Checking for program restart in ESP32
        check = 0
        while check < 1:
            line = ser.readline()
            if b"<<START>>" in line:
                espreboot.off()
                msg1 = {'payload':"sniffer startted"}
                node.send(msg1)
                check += 1
            '''if b"CONNECTED" in line:
                check += 1
                msg2 = {'payload':"WiFi Conncted"}
                node.send(msg2)
            if b"IP ASSIGNED" in line:
                check += 1
                msg3 = {'payload':"IP Assigned to Esp32"}
                node.send(msg3)'''
                
        # Getting Pcap data in to a tempory file        
        pcapfile = "/home/pi/pkt.pcap"
        ssid='WiFi-B2B7'
        psk='44635237'
        p = Process(target=writingPCAP, args=(pcapfile,))
        p.start()
        p_id = p.pid
        with open('data.pickle', 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(p_id, f)
        
        msg4 = {'payload':"Processing started"}
        node.send(msg4)
        
        # Clean the /home/pi/packets/ folder with old pcap files if have any
        shutil.rmtree("/home/pi/packets", ignore_errors=True, onerror=None)
        os.mkdir("/home/pi/packets/")
        
        time.sleep(10)
        
        # Reading the bytes written in to pcapfile and return them to stdout as hexdump
        with subprocess.Popen('tail -f -c +0 {}|tshark -i - -b packets:50 -w "/home/pi/packets/file.pcap"'.format(pcapfile,psk,ssid), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process0:
                
                plist = os.listdir(path='/home/pi/packets/')
                index = 1
                while len(plist) == 0:
                    plist = os.listdir(path='/home/pi/packets/')
                    time.sleep(10)
                while len(plist) != 0:
                   
                    # Break the loop if the time for daily reset
                    now = datetime.now()
                    current_time = now.strftime("%H:%M")
    
                    if current_time == "04:00":
                        break
                        
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
                                msg7 = {'payload':scapy.hexdump(packet,dump=True)}
                                node.send(msg7)
                                #if "32:f7:49:76:28:08" in packet.sprintf("%Dot11.addr2%"):
                                    #msg10 = {'payload':packet.sprintf(" Packet Type = %Dot11.type%\n Packet Subtype = %Dot11.subtype%\n Protocol Version = %Dot11.proto%\n cfe = %Dot11.cfe%\n FCField = %Dot11.FCfield%\n ID = %Dot11.ID%\n addr1 = %Dot11.addr1%\n addr2 = %Dot11.addr2%\n addr3 = %Dot11.addr3%\n SC = %Dot11.SC%\n addr4 = %Dot11.addr4%")+"\nLen = {}".format(packet.wirelen)}
                                    #node.send(msg10)
                                time.sleep(0.20)
                            except Exception as error:
                                msg8 = {'payload':"Error-2: {}".format(error)}
                                node.send(msg8)
                    except Exception as err:
                        msg9 = {'payload':"Error-1: {}".format(err)}
                        node.send(msg9)
                    os.remove(pfilename)
                    index = index + 1
                    time.sleep(4)
                # kill the pcap writing process
                '''msg5 = {'payload':process0.stdout.read()}
                node.send(msg5)
                msg6 = {'payload':process0.stderr.read()}
                node.send(msg6)''' 
                p.terminate()
                process0.terminate()
        time.sleep(60)   
   
                
         
        






