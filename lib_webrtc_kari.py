# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import paho.mqtt.client as mqtt

import sys
import os
import time

drone = ''

broker_ip = 'localhost'
port = 1883

argv = sys.argv
flag = 0

status = 'ON'

lib_mqtt_client = None
control_topic = ''
con = ''
driver = None


def openWeb():
    global driver
    global status

    opt = Options()
    opt.add_argument("--disable-infobars")
    opt.add_argument("start-maximized")
    opt.add_argument("--disable-extensions")
    opt.add_argument('--ignore-certificate-errors')
    opt.add_argument('--ignore-ssl-errors')

    opt.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1
    })

    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}

    try:
        if sys.platform.startswith('win'):  # Windows
            print('Running LIB on Windows')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='C:/Users/dnjst/Downloads/chromedriver')
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):  # Linux and Raspbian
            print('Running LIB on Linux/Rasbian')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/lib/chromium-browser/chromedriver')
        elif sys.platform.startswith('darwin'):  # MacOS
            print('Running browser on MacOS')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/local/bin/chromedriver')
        else:
            print('Running LIB on other OS')
            raise EnvironmentError('Unsupported platform')
    except Exception as e:
        print("Can not found chromedriver..\n", e)
        if sys.platform.startswith('win'):  # Windows
            print('Running LIB on Windows')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='C:/Users/dnjst/Downloads/chromedriver')
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):  # Linux and Raspbian
            print('Running LIB on Linux/Rasbian')
            os.system('sh ./ready_to_WebRTC.sh')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/lib/chromium-browser/chromedriver')
        elif sys.platform.startswith('darwin'):  # MacOS
            print('Running browser on MacOS')
            os.system('sh ./ready_to_WebRTC.sh')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/local/bin/chromedriver')
        else:
            print('Running LIB on other OS')
            raise EnvironmentError('Unsupported platform')

    driver.get("https://kiwi-drone.duckdns.org:8080/demo/vroom")

    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable(('id', 'start')))

    control_web(driver)


def control_web(wd):
    global broker_ip
    global port
    global drone

    msw_mqtt_connect(broker_ip, port)

    wd.find_element("id", 'start').click()
    time.sleep(1)
    username_id = wd.find_element("id", "username")
    username_id.send_keys(drone)
    time.sleep(1)
    username_id.send_keys(Keys.RETURN)

    while True:
        try:
            if wd.find_element('id', 'publish'):
                wd.find_element('id', 'publish').click()
            else:
                pass
        except Exception as e:
            pass


def msw_mqtt_connect(broker_ip, port):
    global lib_mqtt_client
    global control_topic

    lib_mqtt_client = mqtt.Client()
    lib_mqtt_client.on_connect = on_connect
    lib_mqtt_client.on_disconnect = on_disconnect
    lib_mqtt_client.on_subscribe = on_subscribe
    lib_mqtt_client.on_message = on_message
    lib_mqtt_client.connect(broker_ip, port)
    control_topic = '/MUV/control/lib_webrtc/Control'
    lib_mqtt_client.subscribe(control_topic, 0)

    lib_mqtt_client.loop_start()
    return lib_mqtt_client


def on_connect(client, userdata, flags, rc):
    print('[msg_mqtt_connect] connect to ', broker_ip)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    global control_topic
    global con
    global driver
    global flag
    global status

    if msg.topic == control_topic:
        con = msg.payload.decode('utf-8')
        if con == 'ON':
            print('recieved ON message')
            if flag == 0:
                flag = 1
                openWeb()
            elif flag == 1:
                flag = 0
            status = 'ON'
        elif con == 'OFF':
            print('recieved OFF message')
            driver.quit()
            driver = None
            flag = 0
            status = 'OFF'


if __name__ == '__main__':
    drone = argv[1]  # argv[2]  # "KETI_WebRTC"

    time.sleep(1)

    openWeb()
    status = 'ON'
    flag = 1

    # msw_mqtt_connect(broker_ip, port)

# sudo python3 -m PyInstaller -F lib_webrtc_kari.py
