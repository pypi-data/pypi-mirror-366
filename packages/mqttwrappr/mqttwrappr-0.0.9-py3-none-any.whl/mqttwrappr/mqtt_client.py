import yaml
import json
import time
import uuid
import inspect
import paho.mqtt.client as paho




class MessageDispatcher:
    """
    Handles the dispatching of messages via a customizable dispatch function.

    The MessageDispatcher class is responsible for managing the dispatch of
    messages based on a specified function. If no custom function is provided,
    a default dispatch function is used. This class ensures that any custom
    dispatch functions maintain the same signature as the default one to
    guarantee compatibility.

    Attributes:
        dispatch_fnc (Callable[[str, str], None]): The custom or default function
            used for handling message dispatch. If a custom function is provided,
            it must match the signature of the default dispatch function.
    """

    def __init__(self, dispatch_fnc=None):
        """
        Initializes the MessageDispatcher with a custom or default dispatch function.

        Args:
            dispatch_fnc (Callable[[str, str], None], optional): A custom dispatch function.
                Must have the same signature as the default dispatch function.
        """
        if dispatch_fnc is not None:
            if not self._has_same_signature(dispatch_fnc, self.default_dispatch_fnc):
                raise ValueError(
                    "dispatch_fnc must have the same signature as default_dispatch_fnc, with parameters: topic, message.")
            self.dispatch_fnc = dispatch_fnc
        else:
            self.dispatch_fnc = self.default_dispatch_fnc

    @staticmethod
    def default_dispatch_fnc(topic, message):
        """
        Handles the default dispatch function for receiving MQTT messages.

        This static method provides a default implementation for processing MQTT
        messages when a topic and corresponding message are received. The method
        prints the topic and message for debugging or logging purposes.

        Args:
            topic (str): Topic of the MQTT message.
            message (str): The message received for the given topic.
        """
        print(f"[received mqtt] topic: {topic}, message: {message}")

    def dispatch(self, client, topic, message):
        """
        Dispatches a message to the appropriate handler using the provided dispatch function.

        This method serves as the entry point for handling incoming messages. It utilizes
        the dispatch function provided to route the message based on the specified topic.

        Args:
            client (paho.Client): The client instance from which the message originated.
            topic (str): The topic string identifying the category of the message.
            message (str): The content of the message to be dispatched.
        """
        self.dispatch_fnc(topic, message)

    @staticmethod
    def _has_same_signature(func, blueprint_func):
        """
        Determines whether two functions have the same signature based on their parameter definitions.

        This static method compares the parameter signatures of the provided functions to check
        if they match exactly. It is useful for validating that a function adheres to a
        predetermined structure or matches a blueprint function.

        Args:
            func (Callable): The function to be checked.
            blueprint_func (Callable): The function serving as the blueprint for comparison.

        Returns:
            bool: True if the functions have the same signature, False otherwise.
        """
        func_sig = inspect.signature(func)
        blueprint_sig = inspect.signature(blueprint_func)
        return func_sig.parameters == blueprint_sig.parameters


class MqttClient:
    """
    Represents an MQTT client for handling MQTT communication.

    Provides methods for publishing and subscribing to MQTT topics, managing connections,
    and handling MQTT messages. The client abstracts the complexities of the MQTT protocol
    to facilitate easy integration within various applications.

    Attributes:
        client (paho.Client): An instance of the Paho MQTT client.
        client_id (str): The unique identifier assigned to the MQTT client.
        username (str): The username for MQTT broker authentication.
        password (str): The password for MQTT broker authentication.
        broker (str): The address or IP of the MQTT broker.
        port (int): The port number used to connect to the MQTT broker.
        userdata (Any): Optional user data passed to MQTT callbacks.
        protocol (int): The MQTT protocol version. Defaults to MQTT version 5.
        dispatcher (Optional[MessageDispatcher]): The message dispatcher for handling
            incoming MQTT messages.
    """

    def __init__(self, broker: str, port: int, username: str = None, password: str = None, userdata=None,
                 protocol=paho.MQTTv5, client_id: str = None, qos:int = 2, certs: str = None):
        """
        Initializes the MqttClient with the specified broker, port, and optional authentication details.

        Args:
            broker (str): The address or IP of the MQTT broker.
            port (int): The port number to connect to the MQTT broker.
            username (str, optional): The username for MQTT broker authentication.
            password (str, optional): The password for MQTT broker authentication.
            userdata (Any, optional): Optional user data passed to MQTT callbacks.
            protocol (int, optional): The MQTT protocol version. Defaults to MQTT version 5.
            client_id (str, optional): The unique identifier for the MQTT client. If not provided, a random UUID is generated.
            certs (str, optional): Path to CA certificate.
        """
        if client_id is None:
            client_id = str(uuid.uuid4())
            print(f"client_id set to: {client_id}")

        self.client = None
        self.client_id = client_id
        self.username = username
        self.password = password
        self.broker = broker
        self.port = port
        self.userdata = userdata
        self.protocol = protocol
        self.certs = certs
        self._setup_client()
        self.dispatcher = None
        self.qos = qos
        

    @classmethod
    def from_yaml(cls, file_path: str) -> 'MqttClient':
        """
        Creates an instance of MqttClient using a YAML file of parameters and an optional callback dispatch function.

        Args:
            file_path (str): The path to the YAML file containing MQTT configuration details.

        Returns:
            MqttClient: An instance of the MqttClient class created using the provided parameters.
        """
        with open(file_path, 'r') as file:
            info_dict = yaml.safe_load(file)

        return cls(
            client_id=info_dict.get('client_id', None),
            username=info_dict.get('username', None),
            password=info_dict.get('password', None),
            broker=info_dict['broker'],
            port=info_dict['port'],
            certs=info_dict['cafile'],
            userdata=info_dict.get('userdata'),
            protocol=info_dict.get('protocol', paho.MQTTv5)
        )

    def _setup_client(self):
        """
        Sets up the MQTT client with the specified parameters.

        Returns:
            None
        """
        self.client = paho.Client(client_id=self.client_id, userdata=self.userdata, protocol=self.protocol)
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        if self.port == 8883: 
            if self.certs is not None:   
                self.client.tls_set(ca_certs=self.certs)
                self.client.tls_insecure_set(False)
            else:
                self.client.tls_insecure_set(True)

        print(f"[DEBUG] Connecting with client_id={self.client_id}, username={self.username}")

        self.client.connect(self.broker, self.port)


       
        self.client.loop_start()
        

        time.sleep(1)

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback method invoked when a connection attempt is successful.

        Args:
            client (paho.Client): The client object representing the connection.
            userdata (Any): The user data that was previously set for this client.
            flags (dict): The flags associated with the connection.
            rc (int): The return code indicating the success or failure of the connection.
            properties (Optional[dict]): Optional properties associated with the connection.

        Returns:
            None
        """
        print("CONNACK received with code %s." % rc)
        

    def _on_publish(self, client, userdata, mid, properties=None):
        """
        Callback method invoked when a message is successfully published.

        Args:
            client (paho.Client): The client instance for this callback.
            userdata (Any): The private user data as set in `mqtt.Client.user_data_set()`.
            mid (int): The message ID of the successfully published message.
            properties (Optional[dict]): The properties associated with the published message.

        Returns:
            None
        """
        print("published message - mid: " + str(mid))

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """
        Subscribe callback function.

        Args:
            client (paho.Client): The client instance for this callback.
            userdata (Any): The private user data set in `Client()` or `ClientTLS()` constructor.
            mid (int): Message ID of the subscribe request.
            granted_qos (list): List of QoS levels granted by the broker for the requested subscriptions.
            properties (Optional[dict]): Optional message properties associated with the subscription.

        Returns:
            None
        """
        print("Subscribed: " + str(mid) + "; qos: " + str(self.qos))

    def _on_message(self, client, userdata, msg):
        """
        Receive and process an incoming message.

        Args:
            client (paho.Client): The client instance for the connection.
            userdata (Any): The private user data as set in the client constructor or with
                client.user_data_set().
            msg (paho.MQTTMessage): An instance of the MQTTMessage class, representing the received
                message.

        Returns:
            None
        """
        topic = msg.topic
        message = msg.payload.decode('utf-8')

        try:
            # Try to parse the payload as JSON
            data = json.loads(message)
            if isinstance(data, dict):
                message = data
        except json.JSONDecodeError:
            #no dictionary
            pass

        self.dispatcher.dispatch(client=client,
                                 topic=topic,
                                 message=message)
        


    def publish(self, topic: str, message: str or dict= None):
        """
        Publishes a message to a specific topic.

        The method sends either a string message or JSON-formatted dictionary to the specified topic.
        It ensures that the message is correctly formatted and handles cases where the message is not
        provided or has an incompatible type. If a dictionary is provided as a message, it is
        automatically converted to a JSON-formatted string before publishing.

        Args:
            topic (str): The topic to which the message will be published.
            message (str or dict, optional): The message to publish. It can be either a string or a
                dictionary. If a dictionary is provided, it is converted to a JSON-formatted string
                before publishing.

        Raises:
            TypeError: If the message is not a string or a dictionary.

        Returns:
            None
        """


        
        if message is None:
            print("[DEBUG] No message provided, nothing to publish.")
            return

        if isinstance(message, dict):
            message = json.dumps(message)
            print("[DEBUG] Converted dictionary to JSON string for publishing.")
        elif not isinstance(message, str):
            raise TypeError("Message must be a string or a dictionary.")

        print(f"[DEBUG] Publishing to topic: {topic}, message: {message}")
        result = self.client.publish(topic, message, qos=self.qos, retain=True)
        print(f"[DEBUG] Publish result: {result.rc}")  # 0 means success
        time.sleep(1)


    def publish_dict(self, topic: str, data: dict):
        """
        Publishes a dictionary as a JSON string on the specified topic.

        Args:
            topic (str): A string representing the topic to which the dictionary is being published.
            data (dict): A dictionary that needs to be published as a JSON string.

        Note:
            This method is outdated. You can directly send a dictionary to the `publish` function
            by converting it to a JSON string using `json.dumps()` before calling `publish`.
            Example:
                self.publish(topic, json.dumps(your_dict))

        Returns:
            None
        """
        self.client.publish(topic, json.dumps(data), retain=True)

    def subscribe(self, topic: str, dispatch_fnc=None):
        """
        Subscribes to a given topic with specified quality of service level and initializes the message
        dispatching function.

        Args:
            topic (str): The MQTT topic to subscribe to.
            dispatch_fnc (Callable, optional): The function responsible for handling dispatched messages.

        Returns:
            None
        """
        self.dispatcher = MessageDispatcher(dispatch_fnc)
        self.client.subscribe(topic, self.qos)
        self.client.loop_start()

    def publish_on_terminal_input(self):
        """
        Publishes a message to a topic based on user input from the terminal.

        Returns:
            None
        """
        while True:
            message = input("Enter a message to publish or 'exit' to quit:")
            if message.lower() == 'exit':
                break
            topic = input("Enter the topic to publish to:")
            self.client.publish(topic, message)