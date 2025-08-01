
import time
from typing import Callable
import logging

from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion


logger = logging.getLogger(__name__)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print(f"Subscribed with mid {mid} and properties {properties}")


class MQTTConsumer:
    """MQTTConsumer class for consuming messages from an MQTT broker.
    See https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html

    This class extends the Paho MQTT Client and provides methods to handle incoming
    messages and manage the connection to the MQTT broker. It is designed to be used in a threaded
    environment, allowing it to run in the background while processing messages as they arrive.
    """

    def __init__(
            self,
            broker_address: str,
            broker_port: int,
            cbck_on_connect: Callable = on_connect,
            cbck_on_subscribe: Callable = on_subscribe,
            keepalive: int = 60,
            connect_retries: int = 5,
            connect_timeout: int = 1
            ) -> None:
        """Initializes the MQTTConsumer.

        Args:
            broker_address (str): The address of the MQTT broker.
            broker_port (int): The port of the MQTT broker.
            cbck_on_connect (Callable, optional): Callback function for on_connect. Defaults to
                on_connect.
            cbck_on_subscribe (Callable, optional): Callback function for on_subscribe. Defaults to
                on_subscribe.
            keepalive (int, optional): Keepalive interval in seconds. Defaults to 60.
            connect_retries (int, optional): Number of connection retries. Defaults to 5.
            connect_timeout (int, optional): Connection timeout in seconds. Try increasing this if
                you experience connection issues. Defaults to 1.
        """

        self.client = Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=None)
        self.client.on_connect = cbck_on_connect
        self.client.on_subscribe = cbck_on_subscribe

        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.connect_retries = connect_retries
        self.connect_timeout = connect_timeout

    def _connect(self) -> None:
        """Connects to the MQTT broker."""
        while True:
            try:
                logger.info(f"Connecting to MQTT broker at {self.broker_address}:{self.broker_port}")
                self.client.connect(
                    host=self.broker_address,
                    port=self.broker_port,
                    keepalive=self.keepalive)
                time.sleep(self.connect_timeout)
                self.client.loop()
                if self.client.is_connected():
                    logger.info("Connected to MQTT broker successfully.")
                    break

            except Exception as e:
                logger.error(f"Failed to connect to MQTT broker: {e}")
            if self.connect_retries > 0:
                self.connect_retries -= 1
                logger.info(f"Retrying connection... ({self.connect_retries} retries left)")
            else:
                logger.error("Max connection retries reached. Exiting.")
                raise ConnectionError("Could not connect to MQTT broker after multiple attempts.")

    @property
    def is_connected(self) -> bool:
        """Checks if the MQTT client is connected."""
        return self.client.is_connected()

    def _disconnect(self) -> None:
        """Disconnects from the MQTT broker."""
        self.client.disconnect()

    def start(self) -> None:
        """Establishes a connection and starts the MQTT consumer thread."""
        logger.info("Starting MQTT consumer thread...")
        self._connect()
        self.client.loop_start()

    def stop(self) -> None:
        """Stops the MQTT consumer thread."""
        logger.info("Stopping MQTT consumer thread...")
        self._disconnect()

    def add_topic_callback(
            self,
            topic: str,
            callback: Callable) -> None:
        """Adds a callback for a specific topic and subscribes to it.

        Args:
            topic (str): The MQTT topic to subscribe to.
            callback (Callable): The callback function to handle incoming messages.
        """
        if not self.is_connected:
            logger.error("Cannot add topic callback: MQTT client is not connected.")
            return
        def on_message(client, userdata, message):
            msg = message.payload.decode()
            logger.debug(f"Received message on topic {message.topic}: {msg}")
            callback(msg)

        self.client.message_callback_add(
            sub=topic,
            callback=on_message)
        self.client.subscribe(topic)
        logger.info(f"Callback added for topic: {topic}")

    def remove_topic_callback(
            self,
            topic: str) -> None:
        """Removes the callback for a specific topic.

        Args:
            topic (str): The MQTT topic to unsubscribe from.
        """
        if not self.is_connected:
            logger.error("Cannot remove topic callback: MQTT client is not connected.")
            return
        self.client.message_callback_remove(topic)
        self.client.unsubscribe(topic)
        logger.info(f"Callback removed for topic: {topic}")

    def publish(
            self,
            topic: str,
            payload: str,
            qos: int = 0,
            retain: bool = False) -> None:
        """Publishes a message to a specific topic."""
        logger.info(f"Publishing message to topic {topic}: {payload}")
        self.client.publish(
            topic=topic,
            payload=payload,
            qos=qos,
            retain=retain)
