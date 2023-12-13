import RPi.GPIO as GPIO
import requests
import json
import re
import time
import threading
import os
import sys
import subprocess

users = ['account @']
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

LED_PIN = 12
button = 10 

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

previous_like_count = 0
current_like_count = 0


def instagramThread():
    global previous_like_count
    global current_like_count

    for user in users:
        page = requests.get('https://www.instagram.com/' + user + '/', headers=headers)
        #if page.status_code == 200:
         #   print('Success!')
        if page.status_code == 404:
            print('Not Found.')
        
        text = page.text
    
        finder_text_start = ('<script type="text/javascript">'
                                    'window._sharedData = ')
        finder_text_start_len = len(finder_text_start) - 1
        finder_text_end = ';</script>'
    
        all_data_start = text.find(finder_text_start)
        all_data_end = text.find(finder_text_end, all_data_start + 1)
        json_str = text[(all_data_start + finder_text_start_len + 1) \
                            : all_data_end]
        all_data = json.loads(json_str)

        media = list(all_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'])
        current_like_count = media[0]['node']['edge_liked_by']['count']

        if current_like_count > previous_like_count:
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(1)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(1)

        print ('current_like_count')
        previous_like_count = current_like_count


lightBulbOn = False
pressed = False
previousPressed = False

igTimer = time.time()

try:
    while True:

        if GPIO.input(10) == GPIO.LOW:
            pressed = False

        elif GPIO.input(10) == GPIO.HIGH:
            pressed = True
        
        if pressed and not previousPressed:
            lightBulbOn = not lightBulbOn
            GPIO.output(LED_PIN, GPIO.LOW)
            previousPressed = True

        if lightBulbOn:
            GPIO.output(LED_PIN, GPIO.HIGH)
            instagramThread()
            print('instagram')
        else:
            #if time.time() - igTimer > 1:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print('common light bulb activated')
             #   igTimer = time.time()

        previousPressed = pressed


except KeyboardInterrupt:
    GPIO.cleanup()

