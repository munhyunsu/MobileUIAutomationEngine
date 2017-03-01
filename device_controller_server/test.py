from device_controller import DeviceController
import configparser
import os

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

    for apk in apk_list:
        try:
            controller.run_test(apk)
        except Exception as e:
            print(e)
            controller.reboot()
    

if __name__ == '__main__':
    main()
