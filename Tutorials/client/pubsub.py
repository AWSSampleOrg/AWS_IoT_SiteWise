# -*- encoding:utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import os
import json
import sys
import time
import threading
# Third party
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import psutil

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

received_all_event = threading.Event()
actual_received_count = 0
expected_received_count = 10

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a6fojmly8j1zw-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "Thing1"
PATH_TO_CERT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates/output/device_cert_filename.pem")
PATH_TO_KEY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates/output/device_cert_key_filename.key")
PATH_TO_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates/output/AmazonRootCA1.pem")
TOPIC = "test/iot"

def read_performance():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    timestamp = time.time()
    return {"cpu": cpu, "memory": memory, "timestamp": timestamp}

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    logger.debug(f"Connection interrupted. error: {error}")


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    logger.debug(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        logger.debug("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    logger.debug(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    logger.debug(f"Received message from topic '{topic}': {payload}")
    global actual_received_count
    actual_received_count += 1
    if actual_received_count == expected_received_count:
        received_all_event.set()

# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    logger.debug(f"Connection Successful with return code: {callback_data.return_code} session present: {callback_data.session_present}")

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    logger.debug(f"Connection failed with error code: {callback_data.error}")

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    logger.debug("Connection closed")

def get_connection():
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=PATH_TO_CERT,
        pri_key_filepath=PATH_TO_KEY,
        client_bootstrap=client_bootstrap,
        ca_filepath=PATH_TO_ROOT,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=6,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed
    )

    logger.debug("Connecting to %s with client ID '%s'...", ENDPOINT, CLIENT_ID)
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()

    return mqtt_connection

def main():
    mqtt_connection = get_connection()

    logger.debug(f"Subscribing to topic '{TOPIC}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )
    subscribe_result = subscribe_future.result()
    logger.debug(f"Subscribed with qos: {str(subscribe_result['qos'])}, packet_id: {packet_id}")

    for i in range(expected_received_count):
        performance = read_performance()
        data = json.dumps({ "index": i, "performance": json.dumps(performance) })
        logger.debug(data)
        mqtt_connection.publish(topic=TOPIC, payload=data, qos=mqtt.QoS.AT_LEAST_ONCE)
        time.sleep(1)

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if received_all_event.is_set():
        logger.debug("Waiting for all messages to be received...")

    received_all_event.wait()
    print(f"actual_received_count = {actual_received_count}, expected_received_count = {expected_received_count}")

    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()


if __name__ == "__main__":
    main()
