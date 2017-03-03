import subprocess
import time
import configparser
import os
import datetime
import logging

class DeviceController:

    def __init__(self):
        self.init_config()

    def reboot(self):
        """
        단말기 재부팅시키기. adb shell reboot가 안정적인 재부팅 명령어인지는 확인해야한다.
        adb shell reboot 명령어 실행 후, 10초간격으로 adb연결된 device가 있는지 확인(재부팅
        완료되었는지 확인)
        연결을 확인한 후 10초 후 함수 종료
        output
            - 재연결 확인이 완료되면 True반환
        """
        command = adb_location + 'adb shell reboot'
        try:
            proc_reboot = subprocess.Popen(command, shell=True)
            time.sleep(10)
        except Exception as e:
            logging.error(e + ' adb shell reboot error')
            raise e
       
        command = adb_location + 'adb devices'
        while True:
            try:
                proc_check_on = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                output = str(proc_check_on.stdout.read())
                devices = output.split("\\n")
                # 연결된 단말기가 1개 있으면 len이 4
                if len(devices) == 4:
                    time.sleep(10)
                    logging.info('단말기 재연결 확인 완료')
                    break
                else: # 연결된 단말기가 없다면 3으로 나온다.
                    time.sleep(10)
            except Exception as e:
                time.sleep(10)
                continue

        return True

    def init_config(self):
        """
        설정파일 읽어오기
        """
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
        except FileExistsError as e: # 파일이 이미 존재한다면 넘어간다.
            pass
        except Exception as e:
            raise e

    def run_test(self, pkg_name):
        """
        APK파일 이름을 받아서 테스트 진행
        설치 -> 실행 -> Random Test -> 종료 및 삭제 -> pcap,mp4 파일 추출
        install 에서 에러났을경우에만 재부팅 하도록 한다. (단말기 공간이 모두 찼을경우 존재하므로)
        [args]
        pkg_name : 패키지이름(APK파일 이름)
        """
        pcap_name = pkg_name + '.pcap'
    

        try:
            self.install_apk(pkg_name)
        except Exception as e:
            raise e

        command = adb_location + "adb shell su -c " + tcpdump_directory + "tcpdump -i wlan0 -w " + pcap_save_directory + pcap_name + " -s 0"

        try:
            proc_tcpdump = subprocess.Popen(command, shell=True)
        except Exception as e:
            logging.error('proc_tcpdump error. uninstall ' + pkg_name + ' and skip.')
            self.uninstall_app(pkg_name)
            return False

        try:
            self.run_app(pkg_name)
        except Exception as e:
            logging.error('run_app error : ' + e)
            self.uninstall_app(pkg_name)
            return False
        

        try:
            self.close_app(pkg_name)
        except Exception as e:
            logging.error('close_app error : ' + e)
            self.uninstall_app(pkg_name)
            return False

        try:
            proc_tcpdump.kill()
        except Exception as e:
            logging.error('proc_tcpdump.kill error : ' + e)
            self.uninstall_app(pkg_name)
            return False
    
        time.sleep(3)

        try:
            self.pull_pcap(pkg_name)
        except Exception as e:
            logging.error('pull_pcap error : ' + e)
            self.uninstall_app(pkg_name)
            return False

        #har파일은 아직
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
            logging.error('uninstall_app error : ' + e)
            return False

        logging.info(pkg_name + ' testing was finished')
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
        """
        apk파일 이름을 인자로 받아 연결된 단말기에 설치한다.
        """
        apk_name = pkg_name + '.apk'
        mp4_name = pkg_name + '.mp4'
 
        try:
            command = adb_location + "adb install " + apk_directory + apk_name
            data = subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

    def run_app(self, pkg_name):
        """
        앱을 실행시키고 screenrecord도 같이 실행시켜서 영상녹화를 한다.
        """
        mp4_name = pkg_name + '.mp4'
        try:
            # 랜덤테스트 진행시
            command = adb_location + "adb shell screenrecord --time-limit 30 " + pcap_save_directory + mp4_name
            proc_record = subprocess.Popen(command, shell=True)
        except Exception as e:
            raise e
    
        try:
            # 앱 첫화면에 대해서만 진행 할 경우
            command = adb_location + 'adb shell monkey -p ' + pkg_name + ' 1'
            # 랜덤테스트
            # command = adb_location + "adb shell monkey -p " + pkg_name + " --pct-touch 100 --throttle 5000 -v 24"
            proc_monkey = subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

        
        try:
            time.sleep(60)
            proc_record.kill()
            # print('kill')
            time.sleep(2)
        except Exception as e:
            raise e


    def uninstall_app(self, pkg_name):
        """
        인자로 받은 앱을 단말기에서 삭제한다.
        """
        try:
            command = adb_location + "adb uninstall " + pkg_name
            subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e

    def close_app(self, pkg_name): 
        """
        인자로 받은 패키지 이름의 앱을 단말기에서 정지시킨다.
        """
        try:
            command = adb_location + "adb shell am force-stop " + pkg_name
            subprocess.check_call(command, shell=True)
        except Exception as e:
            raise e
