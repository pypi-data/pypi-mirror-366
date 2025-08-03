# mqttwrappr

[![pypi](https://img.shields.io/pypi/v/mqttwrappr.svg)](https://pypi.org/project/mqttwrappr/)
[![versions](https://img.shields.io/pypi/pyversions/mqttwrappr.svg)](https://git-ce.rwth-aachen.de/kls/mqttwrappr)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://git-ce.rwth-aachen.de/kls/mqttwrappr/-/blob/main/LICENSE?ref_type=heads)

This library provides a simple interface for interacting with MQTT brokers using the Paho MQTT client. It includes
classes for managing MQTT connections, publishing messages, and subscribing to topics with customizable message
dispatching.

⚠️ Note: This package is currently in active development. It is not yet feature-complete. Users should expect changes and potential instability.

👥 Please feel free to test and contribute.

## 🚀 Quickstart Example
### Creating an MQTT Client

To create an MQTT client, you can either instantiate it directly or use a YAML configuration file.

#### Creating client

```python
from mqttwrappr import MqttClient

# Create an MQTT client instance
mqtt_client = MqttClient(
    broker='mqtt.example.com',
    port=1883,
    username='your_username',
    password='your_password'
)
```
#### Creating client from config file 
(recommended way)

```yaml
#config.yaml
broker: mqtt.example.com
port: 1883
username: your_username
password: your_password
```

```python
from mqttwrappr import MqttClient

# Create an MQTT client instance from a YAML configuration file
mqtt_client = MqttClient.from_yaml('config.yaml')
```

### Subscribing to a Topic

You can subscribe to a topic and handle incoming messages using a custom dispatch function.
A custom dispatch function is a user-defined function that processes incoming MQTT messages. It serves as a flexible
mechanism to handle messages received from subscribed topics, allowing developers to implement specific logic tailored
to their application's needs. It is crucial that the custom dispatch function accepts exactly two parameters: `topic` and
`message`. The function must be defined with precisely these two parameters—no more, no less—to ensure compatibility with
the MQTT client's dispatch mechanism.

```python
def custom_dispatch(topic, message):
    print(f"Custom Dispatch - Topic: {topic}, Message: {message}")

# Subscribe to a topic with a custom dispatch function
mqtt_client.subscribe(topic='test/topic', qos=1, dispatch_fnc=custom_dispatch)
```

### Publishing Messages

You can publish messages to a topic. Messages can be strings or dictionaries (which are converted to JSON).

```python
# Publish a simple string message
mqtt_client.publish(topic='test/topic', message='Hello, MQTT!')

# Publish a dictionary as a JSON string
mqtt_client.publish(topic='test/topic', message={'key': 'value'})
```

### Interactive Terminal Publishing
You can also publish messages interactively from the terminal.

```python
# Start interactive terminal input for publishing messages
mqtt_client.publish_on_terminal_input()
```

---
*please also check out the [examples](https://git-ce.rwth-aachen.de/kls/mqttwrappr/-/tree/main/examples?ref_type=heads) provided*


## 🔨 Installation
```bash
pip install mqttwrappr
```

if you want to run your own mqtt server check out [setup-mosquitto-with-docker](https://github.com/sukesh-ak/setup-mosquitto-with-docker)

## ©️ License

This project is licensed under
the [MIT License](https://git-ce.rwth-aachen.de/kls/mqttwrappr/-/blob/main/LICENSE?ref_type=heads).
