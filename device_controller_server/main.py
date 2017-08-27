from device_controller import DeviceController
import configparser
import os
import logging
import logging.config


def list_apk(path):
    """
        path를 입력받아 해당 경로에 존재하는 apk파일들을 리스트형태로 가지고온다.
    """
    result = []
    for f in os.listdir(path):
        if f.endswith('.apk'):
            result.append(f.split('.apk')[0])
    return result

def main():
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('device_controller')

    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
    except Exception as e:
        logging.error(e + ' config.ini파일 읽는중에 에러발생')
        raise e

    try:
        apk_directory = config.get('device_controller','apk_directory')
    except Exception as e:
        logging.error(e + ' apk_directory 읽는중 에러 발생')
        raise e

    try:
        apk_list = list_apk(apk_directory)
    except Exception as e:
        logging.error(e + ' apk_list 가지고 오는 중 에러 발생')
        raise e

    controller = DeviceController()

    # 디렉토리 안에 들어있는 모든  APK파일에 대해서 진행
    for apk in apk_list:
        try:
            # APK파일 하나씩 테스트 진행
            controller.run_test(apk)
        except Exception as e:
            continue
            # 발생하는 Exception 종류가 뭐가있나?

if __name__ == '__main__':
    main()
