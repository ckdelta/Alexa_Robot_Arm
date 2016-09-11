import sys
import logging
import time
import json
import getopt
import pprint
import usb.core, usb.util, time
import requests

RoboArm = usb.core.find(idVendor=0x1267, idProduct=0x000)

def MoveArm(Duration, ArmCmd):  # After this, all code until the demo commands must be indented
    ' Function to start the movement '
    RoboArm.ctrl_transfer(0x40, 6, 0x100, 0, ArmCmd, 1000)
    #Stop the movement after waiting a specified duration
    time.sleep(Duration)
    ArmCmd = [0, 0, 0]
    RoboArm.ctrl_transfer(0x40, 6, 0x100, 0, ArmCmd, 1000)

#comm = raw_input("Please enter command: ")
#print "you entered", comm

def perform_pass_sequence():
    MoveArm(0.9, [2, 0, 0])  # Grip open
    MoveArm(7.3, [0, 2, 0])  # Rotate base clockwise by 3.7
    time.sleep(0.2)
    MoveArm(1.7, [128, 0, 0])  # Shoulder down
    time.sleep(0.2)
    MoveArm(0.9, [1, 0, 0])  # Grip close
    MoveArm(2.5, [64, 0, 0])  # Shoulder up
    time.sleep(0.2)
    MoveArm(4.4, [0, 1, 0])  # Rotate base anti-clockwise

def perform_massage_sequence():
    MoveArm(1, [2, 0, 0])  # Grip open
    MoveArm(5.3, [0, 2, 0])  # Rotate base clockwise by 3.7
    time.sleep(0.2)
    MoveArm(1.6, [128, 0, 0])  # Shoulder down
    time.sleep(0.2)
    MoveArm(0.9, [1, 0, 0])  # Grip close
    time.sleep(0.5)
    i = 0
    while i < 10:
        MoveArm(0.8, [2, 0, 0])  # Grip open
        MoveArm(0.9, [1, 0, 0])  # Grip close
        time.sleep(0.5)
        i = i + 1
    MoveArm(0.8, [2, 0, 0])  # Grip open

def peform_recovery_sequence():
    MoveArm(2.5, [64, 0, 0])  # Shoulder up
    time.sleep(0.2)
    MoveArm(8.4, [0, 1, 0])  # Rotate base anti-clockwise

# Loop forever
'''while True:
    comm = raw_input("Please enter another command: ")

    if comm == "pass":
        MoveArm(0.9, [2, 0, 0])  # Grip open
        MoveArm(7.3, [0, 2, 0])  # Rotate base clockwise by 3.7
        time.sleep(0.2)
        MoveArm(1.7, [128, 0, 0])  # Shoulder down
        time.sleep(0.2)
        MoveArm(0.9, [1, 0, 0])  # Grip close
        MoveArm(2.5, [64, 0, 0])  # Shoulder up
        time.sleep(0.2)
        MoveArm(4.4, [0, 1, 0])  # Rotate base anti-clockwise

    if comm == "massage":
        MoveArm(1, [2, 0, 0])  # Grip open
        MoveArm(5.3, [0, 2, 0])  # Rotate base clockwise by 3.7
        time.sleep(0.2)
        MoveArm(1.6, [128, 0, 0])  # Shoulder down
        time.sleep(0.2)
        MoveArm(0.9, [1, 0, 0])  # Grip close
        time.sleep(0.5)
        i=0
        while i < 10:
            MoveArm(0.8, [2, 0, 0])  # Grip open
            MoveArm(0.9, [1, 0, 0])  # Grip close
            time.sleep(0.5)
            i = i + 1
        MoveArm(0.8, [2, 0, 0])  # Grip open
        # if time: perform salutation?


    if comm == "massage_sequence":
        i = 0
        while i < 10:
            MoveArm(0.5, [2, 0, 0])  # Grip open
            MoveArm(0.7, [1, 0, 0])  # Grip close
            time.sleep(0.5)
            i = i + 1

    if comm == "recover":
        MoveArm(2.5, [64, 0, 0])  # Shoulder up
        time.sleep(0.2)
        MoveArm(8.4, [0, 1, 0])  # Rotate base anti-clockwise


    if comm == "rb_anti":
        MoveArm(1.3, [0, 1, 0])  # Rotate base anti-clockwise

    if comm == "rb_anti_2":
        MoveArm(2, [0, 1, 0])  # Rotate base anti-clockwise

    if comm == "rb_anti_3":
        MoveArm(3, [0, 1, 0])  # Rotate base anti-clockwise

    if comm == "rb_anti_4":
        MoveArm(4.3, [0, 1, 0])  # Rotate base anti-clockwise

    if comm == "rb_clock":
        MoveArm(1.3, [0, 2, 0])  # Rotate base clockwise

    if comm == "rb_clock_3":
        MoveArm(3, [0, 2, 0])  # Rotate base clockwise

    if comm == "rb_clock_4":
        MoveArm(7.3, [0, 2, 0])  # Rotate base clockwise by 3.7

    if comm == "shl_up":
        MoveArm(0.2, [64, 0, 0])  # Shoulder up

    if comm == "shl_down_1":
        MoveArm(1.5, [128, 0, 0])  # Shoulder down

    if comm == "shl_up_1":
        MoveArm(1.4, [64, 0, 0])  # Shoulder up

    if comm == "shl_up_2":
        MoveArm(2.5, [64, 0, 0])  # Shoulder up

    if comm == "shl_up_6":
        MoveArm(6, [64, 0, 0])  # Shoulder up

    if comm == "shl_down":
        MoveArm(0.2, [128, 0, 0])  # Shoulder down

    if comm == "elb_up":
        MoveArm(0.5, [16, 0, 0])  # Elbow up

    if comm == "elb_down":
        MoveArm(0.5, [32, 0, 0])  # Elbow down

    if comm == "wrist_up":
        MoveArm(1, [4, 0, 0])  # Wrist up

    if comm == "wrist_up_1":
        MoveArm(0.5, [4, 0, 0])  # Wrist up

    if comm == "wrist_down_0":
        MoveArm(0.2, [8, 0, 0])  # Wrist down

    if comm == "wrist_up_3":
        MoveArm(3, [4, 0, 0])  # Wrist up

    if comm == "wrist_down_3":
        MoveArm(3, [8, 0, 0])  # Wrist down

    if comm == "wrist_down":
        MoveArm(1, [8, 0, 0])  # Wrist down

    if comm == "wrist_down_1":
        MoveArm(0.5, [8, 0, 0])  # Wrist down

    if comm == "grip_open":
        MoveArm(1, [2, 0, 0])  # Grip open

    if comm == "grip_open_1":
        MoveArm(0.5, [2, 0, 0])  # Grip open

    if comm == "grip_close":
        MoveArm(0.9, [1, 0, 0])  # Grip close

    if comm == "light_on":
        MoveArm(1, [0, 0, 1])  # Light on

    if comm == "light_off":
        MoveArm(1, [0, 0, 0])  # Light off'''

'''def IoTShadowCallback_Get(payload, responseStatus, token):
    #myAWSIoTMQTTShadowClient.disconnect()  # diconnect for now
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    print(responseStatus)
    payloadDict = json.loads(payload)
    pprint.pprint(payloadDict) # print what the json dictionary looks like
    print("version: " + str(payloadDict["version"]))
    #payloadDict["state"]["delta"]["Takein"]
    state = payloadDict.get("state")
    delta = state.get("delta")
    print delta
    pass_value = delta.get("Pass")
    if pass_value is None:
        print "Pass bottle  command NOT requested!"
    if pass_value is not None:
        print "Received pass bottle  command requested!"
        perform_pass_sequence()


    takein_value = delta.get("Takein")
    takeout_value = delta.get("Takeout")
    if takein_value is not None:
        print "Takein bottle  command requested!"
        MoveArm(1, [2, 0, 0]) #Grip open
        time.sleep(1)
        MoveArm(1, [1, 0, 0]) #Grip close

    if takeout_value is not None:
        print "Takeout bottle command requested"
        #MoveArm(1, [32, 0, 0]) #Elbow down
        MoveArm(1, [0, 1, 0]) #Rotate base anti-clockwise
        time.sleep(1)
        MoveArm(1, [0, 1, 0])  # Rotate base anti-clockwise
        time.sleep(1)
        MoveArm(1, [2, 0, 0])  # Grip open
        time.sleep(1)
        MoveArm(1, [1, 0, 0])  # Grip close
        # MoveArm(1, [32, 0, 0]) #Elbow down
        # perform action to takeout now'''


get_url = 'https://thingspace.io/get/latest/dweet/for/techcrunch'

post_url = "https://thingspace.io/dweet/for/techcrunch"

# Loop forever
while True:
    print "looping.."
    resp = requests.get(url=get_url, params=None)
    time.sleep(0.2)
    payloadDict = json.loads(resp.text)
    #pprint.pprint(payloadDict)
    state = payloadDict.get("with")
    pprint.pprint(state)
    content = state[0]
    #print dict
    content_value = content.get("content")
    #pprint.pprint(content_value)
    water_value = content_value.get("Water")
    pprint.pprint(water_value)
    pass_value = content_value.get("pass")
    #pprint.pprint(pass_value)
    massage_value = content_value.get("massage")
    pprint.pprint(massage_value)
    #content = state.get("content")
    if pass_value is 1 and water_value > 0:
        print "Pass bottle  command requested!"
        headers = {}
        payload = {'Water': water_value - 1, 'pass': 0}
        res = requests.post(post_url, data=payload, headers=headers)
        perform_pass_sequence()
    '''if pass_value is not None:
        print "Received pass bottle  command requested!"
        #perform_pass_sequence()'''
    if massage_value is 1:
        headers = {}
        payload = {'Massage': massage_value- 1 }
        res = requests.post(post_url, data=payload, headers=headers)
        perform_massage_sequence()
        #peform_recovery_sequence()
    time.sleep(0.1)
#pass



#rb_anti: MoveArm(1, [0, 1, 0]) #Rotate base anti-clockwise
#2. MoveArm(1, [0, 2, 0]) #Rotate base clockwise
#MoveArm(1, [64, 0, 0]) #Shoulder up
#MoveArm(1, [128, 0, 0]) #Shoulder down
#MoveArm(1, [16, 0, 0]) #Elbow up
#MoveArm(1, [32, 0, 0]) #Elbow down
#MoveArm(1, [4, 0, 0]) #Wrist up
#MoveArm(1, [8, 0, 0]) # Wrist down
#MoveArm(1, [2, 0, 0]) #Grip open
#MoveArm(1, [1, 0, 0]) #Grip close
#MoveArm(1, [0, 0, 1]) #Light on
#MoveArm(1, [0, 0, 0]) #Light off
