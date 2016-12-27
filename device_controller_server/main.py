#-*- coding: utf-8 -*-
import socket
import deviceController
import sys
import ConfigParser
reload(sys)
sys.setdefaultencoding('utf-8')


config = ConfigParser.ConfigParser()
config.read('../setting.ini')


har_path = config.get('main','har_path')
pcap_path = config.get('main','pcap_path')
HOST = config.get('main','HOST')
PORT = config.get('main','PORT')


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print('HOST : '+HOST+' PORT : '+PORT)
s.bind((HOST,int(PORT)))
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
                print(data)
            conn.sendall('finished')
            f.close()
            print('finish send har file')

            
            print('read pcap file and send to web server')
            f = open(pcap_path, 'rb')
            data = f.read(1024)
            while (data):
                conn.send(data)
                data = f.read(1024)
            conn.sendall('finished')
            f.close()
            print('finish send pcap file')
            

        conn.close()

        print 'conn close'

    except:
        conn.close()
