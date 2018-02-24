#!/usr/bin/env python3

from device_controller import DeviceController
import os

def main():


    controller = DeviceController()

    # 디렉토리 안에 들어있는 모든  APK파일에 대해서 진행
    for apk in apk_list:
        try:
            # APK파일 하나씩 테스트 진행
            controller.run_test(apk)
        except Exception as e:
            # 예외가 발생한다면 앱 테스팅 중지 후 다음 앱 테스트 실행
            continue

if __name__ == '__main__':
    main()
