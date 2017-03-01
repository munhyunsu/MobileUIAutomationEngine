#-*- coding:utf-8 -*-

import subprocess
import time
import configparser
import os
import datetime

class DeviceController:

    def __init__(self):
        self.init_config()

    def init_config(self):
        try:
            config = configparser.ConfigParser()
            config.read("config.ini")
        except Exception as e:
            raise e

        global adb_location, apk_directory, tcpdump_directory, pcap_2_har_directory,\
            pcap_save_directory, save_directory

        try:
            adb_location = config.get("device_controller","adb_location")
            apk_directory = config.get("device_controller","apk_directory")
            tcpdump_directory = config.get("device_controller", "tcpdump_directory")
            pcap_2_har_directory = config.get("device_controller","pcap_2_har_directory")
            pcap_save_directory = config.get("device_controller","pcap_save_directory")
            save_directory = config.get("device_controller", "save_directory")
            save_directory = save_directory + datetime.datetime.now().strftime('%y%m%d') + '/'

            os.makedirs(save_directory)
        except FileExistsError as e:
            pass
        except Exception as e:
            raise e

    def run_test(self, pkg_name):
        pcap_name = pkg_name + '.pcap'
    
        try:
            self.install_apk(pkg_name)
        except Exception as e:
            print('install_apk error')
            raise e

        command = adb_location + "adb shell su -c " + tcpdump_directory + "tcpdump -i wlan0 -w " + pcap_save_directory + pcap_name + " -s 0"

        try:
            proc_tcpdump = subprocess.Popen(command, shell=True)
        except Exception as e:
            print('proc_tcpdump error')
            self.uninstall_app(pkg_name)
            raise e

        try:
            self.run_app(pkg_name)
        except Exception as e:
            print('run_app error')
            self.uninstall_app(pkg_name)
            raise e
        

        try:
            self.close_app(pkg_name)
        except Exception as e:
            print('close_app error')
            self.uninstall_app(pkg_name)
            raise e

        try:
            proc_tcpdump.kill()
        except Exception as e:
            print('proc_tcpdump.kill error')
            self.uninstall_app(pkg_name)
            raise e
    
        time.sleep(3)

        try:
            self.pull_pcap(pkg_name)
        except Exception as e:
            print('pull_pcap error')
            self.uninstall_app(pkg_name)
            raise e
        """
        try:
            self.pcap_2_har(pkg_name)
        except Exception as e:
            print('pcap_2_har error')
            self.uninstall_app(pkg_name)
            raise e
        """
        try:
            self.uninstall_app(pkg_name)
        except Exception as e:
            print('uninstall_app error')
            raise e

        return True


    def pcap_2_har(self,pkg_name):
        pcap_name = pkg_name + '.pcap'
        har_name = pkg_name + '.har'

        try:
            os.makedirs(save_directory + 'har')
        except FileExistsError as e:
            pass
        except Exception as e:
            raise e

        command = pcap_2_har_directory + 'main.py ' + save_directory + 'pcap/' + pcap_name + ' ' + save_directory + 'har/' + har_name
        try:
            subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

    def pull_pcap(self,pkg_name):
        pcap_name = pkg_name + '.pcap'
        mp4_name = pkg_name + '.mp4'

        try:
            os.makedirs(save_directory + 'pcap')
        except FileExistsError as e:
            pass
        except Exception as e:
            raise e

        try:
            os.makedirs(save_directory + 'record')
        except FileExistsError as e:
            pass
        except Exception as e:
            raise e

        command = adb_location + "adb pull " + pcap_save_directory + pcap_name + ' ' +\
            save_directory + 'pcap/'

        try:
            subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

        try:
            command = adb_location + "adb pull " + pcap_save_directory + mp4_name + ' ' +\
                save_directory + 'record/'
            subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

        time.sleep(2)

        try:
           command = adb_location + "adb shell rm " + pcap_save_directory + '*.mp4'
           subprocess.check_call(command, shell=True)

           command = adb_location + "adb shell rm " + pcap_save_directory + '*.pcap'
           subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

    

    def install_apk(self, pkg_name):
        apk_name = pkg_name + '.apk'
        mp4_name = pkg_name + '.mp4'
 
        try:
            command = adb_location + "adb install " + apk_directory + apk_name
            data = subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

    def run_app(self, pkg_name):
        mp4_name = pkg_name + '.mp4'
        try:
            command = adb_location + "adb shell screenrecord --time-limit 60 " + pcap_save_directory + mp4_name
            print(command)
            proc_record = subprocess.Popen(command, shell=True)
        except Exception as e:
            raise e
    
        try:
            command = adb_location + "adb shell monkey -p " + pkg_name + " --pct-touch 100 --throttle 5000 -v 24"
            proc_monkey = subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

        time.sleep(1)
        try:
            #proc_record.kill()
            #print('kill')
            time.sleep(2)
        except Exception as e:
            raise e


    def uninstall_app(self, pkg_name):    
        try:
            command = adb_location + "adb uninstall " + pkg_name
            subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

    def close_app(self, pkg_name): 
        try:
            command = adb_location + "adb shell am force-stop " + pkg_name
            subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e
