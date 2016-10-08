import subprocess
import time
import ConfigParser


config = ConfigParser.ConfigParser()
config.read("../setting.ini")

adbLocation = config.get("deviceController","adbLocation")
apkDirectory = config.get("deviceController","apkDirectory")
tcpdumpDirectory = config.get("deviceController", "tcpdumpDirectory")
pcapDirectory = config.get("deviceController","pcapDirectory")
pcapToHarDirectory = config.get("deviceController","pcapToHarDirectory")
pcapSaveDirectory = config.get("deviceController","pcapSaveDirectory")

#adbLocation = '/Users/macgongmon/Downloads/android-sdk/platform-tools/'
#apkDirectory = '/Users/macgongmon/Desktop/apk/'
#tcpdumpDirectory = ''
#pcapDirectory = '/Users/macgongmon/Documents/Github/MobilArchive/'
#pcapToHarDirectory = '/Users/macgongmon/Documents/Github/MobilArchive/device_controller_server/pcap2har-master/'
#pcapSaveDirectory = '/storeage/emulated/0/'


def runTest(pkg_name,apk_name):
    pcapName = 'test.pcap'
    installAPK(apk_name)
    command = adbLocation + "adb shell su -c " + tcpdumpDirectory + "tcpdump -i wlan0 -w " + pcapSaveDirectory + pcapName + " -s 0"
    print ('command = ' + command)

    process = subprocess.Popen(command, shell=True)
    #print process # to debug

    runApp(pkg_name)
    closeApp(pkg_name)
    process.kill()

    pullPcap(pcapName)
    pcapToHar(pcapName)

    uninstallApp(pkg_name)


def pcapToHar(pcapName):
    command = pcapToHarDirectory + 'main.py ' + pcapName + " test.har"
    print (command)
    subprocess.check_call(command, shell=True)


def pullPcap(pcapName):
    command = adbLocation + "adb pull " + pcapSaveDirectory + pcapName
    print (command)
    subprocess.check_call(command, shell=True)

    command = adbLocation + "adb shell rm " + pcapSaveDirectory + "screen.mp4"
    print (command)
    subprocess.check_call(command, shell=True)


def installAPK(apk_name):
    print ('==================== install APK ' + apk_name + '====================')
    print ('APK Name : ' + apk_name)

    command = adbLocation + "adb install " + apkDirectory + apk_name
    print ('command : ' + command)

    data = subprocess.check_call(command, shell=True)
    print (data)

    print ('==================== finish APK installition ====================\n\n\n')


def runApp(pkg_name):
    print ('==================== run App ' + pkg_name + '====================')

    command = adbLocation + "adb shell screenrecord " + tcpdumpDirectory + "screen.mp4"
    print(command)
    record = subprocess.Popen(command, shell=True)

    command = adbLocation + "adb shell monkey -p " + pkg_name + " --pct-touch 100 --throttle 1000 100"
    print ('command : ' + command)

    proc_monkdy = subprocess.check_call(command, shell=True)
    record.kill()

    print ('==================== finish run application ====================\n\n\n')
    return record


def uninstallApp(pkg_name):
    print ('==================== uninstall App ' + pkg_name + '====================')

    command = adbLocation + "adb uninstall " + pkg_name
    print ('command : ' + command)

    subprocess.check_call(command, shell=True)

    print ('==================== finish uninstall application ====================\n\n\n')


def closeApp(pkg_name):
    print ('==================== close App ' + pkg_name + '====================')

    command = adbLocation + "adb shell am force-stop " + pkg_name
    print ('command : ' + command)
    subprocess.check_call(command, shell=True)

    print ('==================== finish close application ====================\n\n\n')
