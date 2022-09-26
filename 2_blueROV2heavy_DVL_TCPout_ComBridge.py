"""
Created on Thu Nov  4 20:23:19 2021

@author: Acoustics_NDST
"""

import socket
import json 
import time
import math 
from datetime import datetime


# connect to DVL socket            
dvl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
dvl_socket.connect(('192.168.3.204', 16171)) 
# Set buffer size for single DVL socket recv
buffer_size = 4096 # message size


# Set host and port for hypack computer socket connection        
HOST = '192.168.3.21'  # IP for the PC running this script
PORT = 6020       # Port to listen on
        
#Initialized TCP socket object
while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print(f'Starting TCP server for BlueROV data at IP address {HOST} and port {PORT}')
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    # Get dvl messages
                    dvl_packet = dvl_socket.recv(buffer_size).decode()
                    message_parts = dvl_packet.split("\r\n")
                    # Filter for velocity message type
                    vel_messages = list(filter(lambda x:'velocity' in x, message_parts))
                    # If there is at least one velocity message, 
                    if len(vel_messages) > 1:
                        # grab the second message, first could be incomplete
                        message_string = vel_messages.pop(1)
                        # read json
                        data = json.loads(message_string)
                        # Get variables        
                        altitude = data["altitude"]
                        speed = math.sqrt(data["vx"]**2 + data["vy"]**2 + data["vz"]**2) 
                        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # Create string of variables
                        output = str("$DVLDATA," + str(dt)  + "," + str(altitude) + "," + str(speed) + "\r\n")
                        print(output)
                        # send
                        conn.sendall(output.encode())  #Send the concatenated string to the client socket
                    time.sleep(.25)  #Repeat this message 4 times per second
    except:
        pass
        

