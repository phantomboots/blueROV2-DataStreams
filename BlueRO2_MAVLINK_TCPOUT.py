"""
Created on Thu Nov  4 20:23:19 2021

@author: Acoustics_NDST
"""

import socket
import requests
import time
from datetime import datetime


HOST = '192.168.3.21'  # IP for the PC running this script
PORT = 6000       # Port to listen on

#Initialized TCP socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Starting TCP server for BlueROV data at IP address {HOST} and port {PORT}')
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            resp = requests.get('http://192.168.3.200:6040/mavlink')
            #This response is a server-side 'Bad Request'; in our case means there is missing data values for lat/long
            if resp.status_code == 200:
                data = resp.json()
                heading = data["vehicles"]["1"]["components"]["1"]["messages"]["VFR_HUD"]["message"]["heading"]   #This is heading.
                depth_mm = data["vehicles"]["1"]["components"]["1"]["messages"]["GLOBAL_POSITION_INT"]["message"]["relative_alt"]  #This the depth parameter
                depth_m = depth_mm / -1000
                output = str("$BLUDATA," + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "," + str(heading) + "," + str(depth_m) + "\r\n")
                print(output)
                conn.sendall(output.encode())  #Send the concatenated string to the client socket
            if resp.status_code != 200 and resp.status_code != 400:
                 # This means something went wrong.
                 raise Exception('Error Code {}'.format(resp.status_code))

            time.sleep(0.25)  #Repeat this message 4 times per second.
            