#Alexa in TecgCrunch Hackathon 2016
from __future__ import print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import datetime
import json

#Setup Login keys
host = "a2bvtjvd2b5lcg.iot.us-east-1.amazonaws.com"
rootCAPath =  "aws-iot-rootCA.crt""
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
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(10)  # 10 sec

#-----------------------------------lambda functions---------------------------#
def lambda_handler(event, context):
    if 'session' in event:
        print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
        if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.e23e8c9e-f738-48dd-bbdb-d51978835364"):
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
    elif intent_name == "CheckStatus":
        return Welcome_response(intent, session)
    elif intent_name == "Massage":
        return Massage_response(intent, session)
    elif intent_name == "FunctionTest":
        return Function_response(intent, session)
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
