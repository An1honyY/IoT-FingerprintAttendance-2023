# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "aews10ygtx382-ats.iot.ap-southeast-2.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERTIFICATE = "/home/pi/certs/certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "/home/pi/certs/private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "/home/pi/certs/AmazonRootCA1.pem"
MESSAGE = "Hello World"
TOPIC = "test/testing"
RANGE = 20

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERTIFICATE,
            pri_key_filepath=PATH_TO_PRIVATE_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=18000   # 5 hrs until disconnect timer
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
        
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")

def test_function():
    # Publish message to server desired number of times.
    print('Begin Publish')
    for i in range (RANGE):
        data = "{} [{}]".format(MESSAGE, i+1)
        message = {"message" : data}
        mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
        print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
        t.sleep(0.1)
    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()

def publish_attendance(name, scan_time, scan_date, class_session):
    topic = "iot/attendance"
    message = {"name":name, "time":scan_time, "date":scan_date, "class":class_session}
    payload = json.dumps(message)
    qos = mqtt.QoS.AT_LEAST_ONCE
    mqtt_connection.publish(topic, payload, qos)
    print("Published: '" + str(payload) + "' to the topic: '" + topic +"'")
    
def publish_motion_detected(motion_time, motion_date, class_session):
    topic = "iot/motion"
    message = {"time":motion_time, "date":motion_date,  "class":class_session}
    payload = json.dumps(message)
    qos = mqtt.QoS.AT_LEAST_ONCE
    mqtt_connection.publish(topic, payload, qos)
    print("Published: '" + str(payload) + "' to the topic: '" + topic+"'")

def close_connection():
    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
