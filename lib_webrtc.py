# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import paho.mqtt.client as mqtt

import sys
import os

display_name = ''
host = ''

broker_ip = 'localhost'
port = 1883

presenter_key = ''
stop_key = ''

argv = sys.argv
flag = 0


def openWeb():
    global display_name
    global host
    global presenter_key
    global stop_key
    global driver

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
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='C:/Users/dnjst/Downloads/chromedriver')
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):  # Linux and Raspbian
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/lib/chromium-browser/chromedriver')
        elif sys.platform.startswith('darwin'):  # MacOS
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/local/bin/chromedriver')
        else:
            raise EnvironmentError('Unsupported platform')
    except Exception as e:
        print("Can not found chromedriver..\n", e)
        if sys.platform.startswith('win'):  # Windows
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='C:/Users/dnjst/Downloads/chromedriver')
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):  # Linux and Raspbian
            os.system('sh ./ready_to_WebRTC.sh')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/lib/chromium-browser/chromedriver')
        elif sys.platform.startswith('darwin'):  # MacOS
            os.system('sh ./ready_to_WebRTC.sh')
            driver = webdriver.Chrome(chrome_options=opt, desired_capabilities=capabilities,
                                      executable_path='/usr/local/bin/chromedriver')
        else:
            raise EnvironmentError('Unsupported platform')

    driver.get("https://{0}/drone?id={1}".format(host, display_name))
    control_web(driver)


def control_web(driver):
    global display_name
    global host
    global broker_ip
    global port
    global presenter_key
    global stop_key

    msw_mqtt_connect(broker_ip, port)

    while True:
    #     Room_Number = driver.find_element_by_id('roomnumber')
    #     # Room_Number.send_keys(room_number)
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
    global presenter_key
    global stop_key
    global driver
    global flag

    if msg.topic == control_topic:
        con = msg.payload.decode('utf-8')
        if con == 'ON':
            print('recieved ON message')
            if flag == 0:
                flag = 1
                openWeb()
            elif flag == 1:
                flag = 0
        elif con == 'OFF':
            print('recieved OFF message')
            driver.quit()
            driver = None


if __name__ == '__main__':

    display_name = argv[2]  # argv[2]  # "KETI_WebRTC"
    host = argv[1]  # argv[1]  # 13.209.34.14

    openWeb()


# sudo python3 -m PyInstaller -F lib_webrtc.py
