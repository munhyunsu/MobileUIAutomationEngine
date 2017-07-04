import subprocess
import time
import configparser
import os
import datetime
import logging
from xml.etree.ElementTree import parse

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
            logging.error(' adb shell reboot error')
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

        global adb_location, apk_directory, tcpdump_directory,\
            pcap_save_directory, save_directory

        try:
            adb_location = config.get("device_controller","adb_location")
            apk_directory = config.get("device_controller","apk_directory")
            tcpdump_directory = config.get("device_controller", "tcpdump_directory")
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
        
        # 데이터를 수집할 디렉토리가 없다면 미리 생성
        # 이미 디렉토리가 존재한다면 pass
        try:
            os.makedirs(save_directory + 'pcap')
            os.makedirs(save_directory + 'record')
            os.makedirs(save_directory + 'xml/' + pkg_name)
        except FileExistsError as e:
            pass
        except Exception as e:
            raise e

        try:
            pcap_name = pkg_name + '.pcap' 
            apk_name = pkg_name + '.apk'
            mp4_name = pkg_name + '.mp4'

            # apk파일 설치
            command = adb_location + "adb install " + apk_directory + apk_name
            subprocess.check_call(command, shell=True)
    
            # tcpdump 실행(Popen으로 Background로 실행)
            command = adb_location + "adb shell su -c " + tcpdump_directory + "tcpdump -i wlan0 -w " +\
                pcap_save_directory + pcap_name + " -s 0"
            proc_tcpdump = subprocess.Popen(command, shell=True)

            # 화면 녹화 시작시간 파악
            initial_time = datetime.datetime.now()

            # 화면 녹화(Popen으로 Background로 실행) 
            command = adb_location + "adb shell screenrecord " + pcap_save_directory + mp4_name
            proc_record = subprocess.Popen(command, shell=True)
    
            # monkey로 이벤트를 발생시키면서 uiautomator로 관찰
            event_index = 0
            prev_count = -1
            count = 0

            # 총 5개의 이벤트 발생
            num_of_event = 5
            while(event_index < num_of_event):
                command = adb_location + "adb shell monkey -p " + pkg_name + " --pct-touch 100 3"
                subprocess.check_call(command, shell=True)
                time.sleep(2)
                while(True):
                    # uiautomator를 batch job으로 무한반복시키면서 node 개수 파악 
                    snap_time = datetime.datetime.now() - initial_time
                    command = adb_location + "adb shell su -c uiautomator dump /sdcard/xml/" + str(int(snap_time.total_seconds())) +\
                        ".xml"
                    subprocess.check_call(command, shell=True)

                    command = adb_location + "adb pull /sdcard/xml/" + str(int(snap_time.total_seconds())) + ".xml " +\
                        save_directory + 'xml/' + pkg_name + '/'
                    subprocess.check_call(command, shell=True)

                    # xml파일 파싱하여 node 개수 파악
                    tree = parse(save_directory + 'xml/' + pkg_name + '/' + str(int(snap_time.total_seconds())) + ".xml")
                    root = tree.getroot()
                    iterator =  root.iter()

                    node_count = 0
                    for item in iterator:
                        node_count = node_count + 1

                    # 이전 xml파일과 노드개수가 불일치하면 아직 렌더링중이므로 노드개수 갱신
                    if(prev_count != node_count):
                        prev_count = node_count
                        count = 0
                    else:
                        count = count + 1

                    # 노드개수가 5개의 xml파일동안 동일하면 렌더링 완료
                    if(count == 5):
                        print('event detected')
                        break

                event_index = event_index + 1

                
            # 앱 종료 및 화면녹화 종료
            if(proc_record.poll() is None):
                proc_record.kill()
            if(proc_tcpdump.poll() is None):
                proc_tcpdump.kill()

            command = adb_location + "adb shell am force-stop " + pkg_name
            subprocess.check_call(command, shell=True)

            # pcap파일 pull
            command = adb_location + "adb pull " + pcap_save_directory + pcap_name + ' ' +\
                save_directory + 'pcap/'
            subprocess.check_call(command, shell=True)

            # mp4파일 pull
            command = adb_location + "adb pull " + pcap_save_directory + mp4_name + ' ' +\
                save_directory + 'record/'
            subprocess.check_call(command, shell=True)


            # 단말기 내부의 mp4파일 삭제
            command = adb_location + "adb shell rm " + pcap_save_directory + '*.mp4'
            subprocess.check_call(command, shell=True)

            # 단말기 내부의 pcap파일 삭제
            command = adb_location + "adb shell rm " + pcap_save_directory + '*.pcap'
            subprocess.check_call(command, shell=True)

            # 단말기의 앱 삭제
            command = adb_location + "adb uninstall " + pkg_name
            subprocess.check_call(command, shell=True)
            logging.info(pkg_name + ' testing was finished')

        except Exception as e:
            raise e
