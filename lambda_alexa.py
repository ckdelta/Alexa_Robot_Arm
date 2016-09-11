#Alexa in TecgCrunch Hackathon 2016
#Lesson1:
#AWSIoTPythonSDK only allows one connection one time, so always disconnect after one access

from __future__ import print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import datetime
import json

#Setup Login keys
host = "a2bvtjvd2b5lcg.iot.us-east-1.amazonaws.com"
rootCAPath =  "aws-iot-rootCA.crt"
certificatePath = "cert.pem"
privateKeyPath = "privkey.pem"
shadowClient = "pi_arm"

# Init AWSIoTMQTTClient
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(shadowClient)
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(30)  # 30 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(30)  # 10 sec

#-----------------------------------lambda functions---------------------------#
def lambda_handler(event, context):
    if 'session' in event:
        print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
        if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.aae9596c-c340-47b3-9af6-21ee130ead0d"):
            raise ValueError("Invalid Application ID")
        if event['session']['new'] and 'requestId' in event['request']:
            print("New session starts with ID: " + event['request']['requestId'])

    if 'request' in event:
        if event['request']['type'] == "LaunchRequest":
            return launch_req(event['request'], event['session'])
        elif event['request']['type'] == "IntentRequest":
            return intent_req(event['request'], event['session'])
        elif event['request']['type'] == "SessionEndedRequest":
            return session_ended_req(event['request'], event['session'])


#------------------------------------------Request type parsing---------------#
#LaunchRequest function
def launch_req(request, session):
    print("LaunchRequest ID: " + request['requestId'] + ", session ID: " + session['sessionId'])
    # Start of launch, send to welcome function
    intent = request
    return Welcome_response(intent, session)

#IntentRequest function
def intent_req(request, session):
    print("IntentRequest ID: "+ request['requestId'] + ", session ID: " + session['sessionId'])
    intent=request['intent']
    intent_name = request['intent']['name']
    #Parse request and send to different functions
    #May add/replace for different apps
    if intent_name == "TakeInItem":
        return In_response(intent, session)
    elif intent_name == "TakeOutItem":
        return Out_response(intent, session)
    elif intent_name == "PassItem":
        return Pass_response(intent, session)
    elif intent_name == "CheckStatus":
        return Welcome_response(intent, session)
    elif intent_name == "Massage":
        return Massage_response(intent, session)
    elif intent_name == "StopIntent":
        return Stop_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return Stop_response()
    elif intent_name == "HelpIntent":
        return Welcome_response(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return Welcome_response(intent, session)
    else:
        raise ValueError("Invalid intent")

#SessionEndedRequest function
def session_ended_req(request, session):
    print("SessionEndedRequest ID: "+ request['requestId'] + ", session ID: " + session['sessionId'])
    return Stop_response()

#-----------------------------------Intent Request Parsing--------------------#
def Welcome_response(intent, session):
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("pi_arm", True)
    customCallback = ""

	# Init Speech
    speech_output = "Welcome to robot arm. " \
                    "You have nothing in stock."   \
                    "Please stock up or ask for help."
    reprompt_text = "Please put in new items. "

    # Set other parameters
    card_title = "Welcome"
    should_end_session = False
    Item_takein=""

	# Get Session Attributes
    if 'attributes' in session:
        if session['attributes']['Item_stock'] != "":
            Item_takein = session['attributes']['Item_stock']
			#Speech
            speech_output = "Welcome to robot arm, " \
                    "You have one" + Item_takein + "in your refrigerator."
            reprompt_text = "Refrigerator Status:" \
                    "You have one" + Item_takein + "in your refrigerator."

	# Send response back to ASK
    session_attributes = create_attributes(Item_takein)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def In_response(intent, session):
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("pi_arm", True)
    customCallback = ""

    # Set other defaults
    card_title = "Item_takein"
    should_end_session = False
    Item_takein = ""

    # Item from slots
    if 'slots' in intent:
        if 'Item' in intent['slots']:
            if 'value' in intent['slots']['Item']:
                Item_takein = intent['slots']['Item']['value'].upper()

    if Item_takein == "":
        print("Warning: there is no item to take in!!!")

    # Build the speech
    speech_output = "Robot Arm is taking in " + Item_takein + ", Please wait. "
    reprompt_text =  Item_takein + "is putting in stock!"

    # Publish to AWS IoT Shadow
    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"Takein\": \"ON\", "\
                                                    "\"Takeout\": \"OFF\", "\
                                                    "\"Massage\": \"OFF\", "\
                                                    "\"Pass\": \"OFF\", "\
                                                    "\"Item\": \"" + Item_takein + "\" "\
                                                "} "\
                                    ", \"reported\": {"\
                                                    "\"Takein\": \"OFF\", "\
                                                    "\"Takeout\": \"OFF\", "\
                                                    "\"Massage\": \"OFF\", "\
                                                    "\"Pass\": \"OFF\" "\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    myAWSIoTMQTTShadowClient.disconnect()

    # Send response back to ASK
    session_attributes = create_attributes(Item_takein)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def Out_response(intent, session):
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("pi_arm", True)
    customCallback = ""

    # Set other defaults
    card_title = "Item_takeout"
    should_end_session = False
    Item_takein=""

    # Item taking out from slots
    if 'slots' in intent:
        if 'Item' in intent['slots']:
            if 'value' in intent['slots']['Item']:
                Item_takeout = intent['slots']['Item']['value'].upper()

    # Item stored in attributes
    if 'attributes' in session:
        if 'Item_stock' in session['attributes'] is not "":
            Item_takein = session['attributes']['Item_stock']

    # Check if target is in stock and set voice
    if Item_takeout == Item_takein:
        # Speech
        speech_output = "Robot Arm is taking out " + Item_takeout + ", Please wait. "
        reprompt_text =  Item_takeout + "is getting out of stock!"
        # Clear stock, !!Need to change to list remove element
        Item_takein=""
        # Publish to AWS IoT Shadow
        myJSONPayload = "{ \"state\" : {"\
                                        "\"desired\": {"\
                                                        "\"Takein\": \"OFF\", "\
                                                        "\"Takeout\": \"ON\", "\
                                                        "\"Massage\": \"OFF\", "\
                                                        "\"Pass\": \"OFF\", "\
                                                        "\"Item\": \"" + Item_takein + "\" "\
                                                    "} "\
                                        ", \"reported\": {"\
                                                        "\"Takein\": \"OFF\", "\
                                                        "\"Takeout\": \"OFF\" "\
                                                    "} "\
                                        "} "\
                        "}"
        myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
        myAWSIoTMQTTShadowClient.disconnect()
    else:
        # Speech
        speech_output = "There is no " + Item_takeout + "in stock. " \
                        "Please check inventory status and change your command."
        reprompt_text =  Item_takeout + "is not in stock!"

    # Send response back to ASK
    session_attributes = create_attributes(Item_takein)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def Pass_response(intent, session):
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("pi_arm", True)
    customCallback = ""

    # Set other defaults
    card_title = "Pass_Item"
    should_end_session = False

    # Item taking out from slots
    if 'slots' in intent:
        if 'Item' in intent['slots']:
            if 'value' in intent['slots']['Item']:
                Item_takeout = intent['slots']['Item']['value'].upper()

    # Speech
    speech_output = "Robot Arm is taking out " + Item_takeout + ", Please wait. "
    reprompt_text =  Item_takeout + "is taken out of stock!"
    # Clear stock, !!Need to change to list remove element
    Item_takein=""
    # Publish to AWS IoT Shadow
    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"Takein\": \"OFF\", "\
                                                    "\"Takeout\": \"OFF\", "\
                                                    "\"Massage\": \"OFF\", "\
                                                    "\"Pass\": \"ON\", "\
                                                    "\"Item\": \"" + Item_takeout + "\" "\
                                                "} "\
                                    ", \"reported\": {"\
                                                    "\"Takein\": \"OFF\", "\
                                                    "\"Pass\": \"OFF\", "\
                                                    "\"Takeout\": \"OFF\" "\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    myAWSIoTMQTTShadowClient.disconnect()

    # Send response back to ASK
    session_attributes = create_attributes(Item_takeout)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def Massage_response(intent, session):
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("pi_arm", True)
    customCallback = ""

    # Set other defaults
    card_title = "Massage"
    should_end_session = False
    Item_takein=""

    # Item stored in attributes
    if 'attributes' in session:
        if 'Item_stock' in session['attributes'] is not "":
            Item_takein = session['attributes']['Item_stock']

    # Speech
    speech_output = "Robot Arm is massaging, enjoy. "
    reprompt_text =  "Enjoy your massaging!"

    # Publish to AWS IoT Shadow
    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"Takein\": \"OFF\", "\
                                                    "\"Takeout\": \"OFF\", "\
                                                    "\"Massage\": \"ON\", "\
                                                    "\"Pass\": \"OFF\", "\
                                                    "\"Item\": \"" + Item_takein + "\" "\
                                                "} "\
                                    ", \"reported\": {"\
                                                    "\"Massage\": \"OFF\" "\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    myAWSIoTMQTTShadowClient.disconnect()

    # Send response back to ASK
    session_attributes = create_attributes(Item_takein)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def Stop_response():
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("pi_arm", True)
    customCallback = ""

    # Set other defaults
    card_title = "Stop"
    should_end_session = True
    Item_takein=""

    #Speech
    speech_output = "Robot Arm is going to power off."
    reprompt_text =  "Powering off."

    # Publish to AWS IoT Shadow
    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"Takein\": \"OFF\", "\
                                                    "\"Takeout\": \"OFF\", "\
                                                    "\"Massage\": \"OFF\", "\
                                                    "\"Pass\": \"OFF\", "\
                                                    "\"Item\": \"" + Item_takein + "\" "\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    myAWSIoTMQTTShadowClient.disconnect()

    # Send response back to ASK
    session_attributes = create_attributes(Item_takein)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


#---------------------Response create functions-------------------------------#
def create_attributes(Item_takein):
    return {"Item": Item_takein.upper()}


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
