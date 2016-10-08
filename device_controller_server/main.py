#-*- coding: utf-8 -*-
import socket
import deviceController
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

HOST = '168.188.129.206'
PORT = 8080

har_path = "/home/dbgustlr92/Desktop/MobilArchive/device_controller_server/test.har"

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((HOST, PORT))
s.listen(1)

while True:

    try:
        conn, addr = s.accept()
        print ('address : ', addr)

        received_data = conn.recv(1024)
        if not received_data:
            break
        elif received_data == 'runTest':  # first parameter is runTest (run the testing)
            print ('====== run Test ======')
            conn.sendall('ack')

            pkg_name = conn.recv(1024)  # app_info[0] : apk name , app_info[1] : activity name
            if not pkg_name:
                break
            print ('pkg name : ', pkg_name)
            conn.sendall('ack')

            apk_name = conn.recv(1024)
            if not apk_name:
                break;
            print ('apk name : ', apk_name)
            # Run test and convert pcap to har file 
            deviceController.runTest(pkg_name, apk_name)

            print ('read har file and send to web server')
            f = open(har_path, 'rb')
            data = f.read(1024)
            while (data):
                conn.send(data)
                data = f.read(1024)
            conn.sendall('finished')
            f.close()
            print('finish send har file')
        conn.close()

        print 'conn close'

    except:
        conn.close()
