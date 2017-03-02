from device_controller import DeviceController
import configparser
import os
import logging

def list_apk(path):
    result = []
    for f in os.listdir(path):
        if f.endswith('.apk'):
            result.append(f.split('.apk')[0])
    return result

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    apk_directory = config.get('device_controller','apk_directory')

    
    apk_list = list_apk(apk_directory)

    controller = DeviceController()

    # 디렉토리 안에 들어있는 모든  APK파일에 대해서 진행
    for apk in apk_list:
        try:
            # APK파일 하나씩 테스트 진행
            controller.run_test(apk)
        except Exception as e:
            # 발생하는 Exception 종류가 뭐가있나?
            print(e)
            controller.reboot()
    

if __name__ == '__main__':
    main()
