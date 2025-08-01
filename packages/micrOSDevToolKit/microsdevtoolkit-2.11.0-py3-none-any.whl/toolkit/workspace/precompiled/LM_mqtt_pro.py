# async_message.py Test of asynchronous mqtt client with async Broker class
# (C) Copyright Peter Hinch 2024.
# Released under the MIT licence.
# Public brokers https://github.com/mqtt/mqtt.github.io/wiki/public_brokers
# mip command: ???

from Config import cfgget
from mqtt_as import MQTTClient, config
from Common import micro_task, console, syslog, exec_cmd


# Set up MQTT
class MQTT:
    CLIENT:MQTTClient = None        # MQTT Client (broker) instance
    TOPIC = "micros"                # Default topic
    TOPIC_COMMAND_LUT = {}          # Lookup table for command/topic pairs
    # Example:
    #       {"topic1": ["mod func", "mod2 func"], "topic2": []}


async def _receiver(task):
    """
    MQTT AS receiver loop
    """
    async for topic, msg, retained in MQTT.CLIENT.queue:
        topic, msg = topic.decode(), msg.decode()
        console(f'Topic: "{topic}" Message: "{msg}" Retained: {retained}')

        # Command execution... use MQTT.TOPIC_COMMAND_LUT
        topic_commands:list = MQTT.TOPIC_COMMAND_LUT.get(topic, None)
        output_struct:list = []
        if topic_commands is None:
            syslog(f"[WARN] mqtt Unknown topic: {topic}")
        elif len(topic_commands) == 0:
            syslog(f"[WARN] mqtt No commands for {topic}")
        else:
            task.out = f"Handle topic: {topic}"
            for cmd in topic_commands:
                single_command = cmd.split()
                if len(single_command) > 0:
                    state, output = exec_cmd(single_command, jsonify=True, skip_check=True)
                    output_struct.append({"state": state, "result": output, "cmd": cmd})
            if len(output_struct) > 0:
                console(f'\tMQTT Publish: {output_struct}')
                task.out = f"Publish {topic}"
                MQTT.CLIENT.publish(topic, str(output_struct))
            else:
                task.out = f"Nothing to publish {topic}"
        task.feed()


async def _subscribe():
    """
    MQTT AS Topic subscribe towards server
    """
    with micro_task(tag="mqtt.subscribe") as my_task:
        my_task.out = "Started"
        try:
            for t in MQTT.TOPIC_COMMAND_LUT:
                console(f"Subscribe topic: {t}")
                await MQTT.CLIENT.subscribe(t, 1)
            my_task.out = "Done"
        except Exception as e:
            my_task.out = f"Error: {e}"


async def _publish(message, topic):
    """
    Send message to topic with mqtt
    """
    tag = f"mqtt.publish.{topic}"
    with micro_task(tag=tag) as my_task:
        console(f"mqtt send: [{topic}] {message}")
        await MQTT.CLIENT.publish(topic, message, qos=1)
        my_task.out = "Sent"


async def _up():
    """
    UP Listener - resubscribe
    """
    with micro_task(tag="mqtt.up") as my_task:
        while True:
            # Wait for UP Event - (re)subscribe
            my_task.out = "Wait"
            await MQTT.CLIENT.up.wait()
            MQTT.CLIENT.up.clear()
            micro_task(tag="mqtt.subscribe", task=_subscribe())
            my_task.out = "Re-Subscription"
            my_task.feed()


async def _init_client(topic:str=None, commands:str=None, raw_dict:dict|None=None):
    """
    Initialize main mqtt receiver and topics
    :param topic: topic string, ex.: 'lights'
    :param commands: semicolon separated commands. ex.: 'rgb toggle; cct toggle'
    OR
    :param raw_dict: python dict string for multi topic subscription, ex.: {"lights": ["rgb toggle", "cct toggle"], ...}
    """
    with micro_task(tag="mqtt.client") as my_task:
        try:
            await MQTT.CLIENT.connect()
            my_task.out = "Connection successful."
        except OSError:
            my_task.out = "Connection failed."
            return
        # Wait for mqtt client connected successfully
        await MQTT.CLIENT.up.wait()
        MQTT.CLIENT.up.clear()
        # Initialize mqtt topics, ha
        subscribe(topic, commands, raw_dict)
        micro_task(tag="mqtt.up", task=_up())
        # Async listener loop
        await _receiver(my_task)
        my_task.out = "Receiver closed"
    # Close when listener exits
    MQTT.CLIENT.close()

#########################################
#           PUBLIC FUNCTIONS            #
#########################################

def publish(message:str, topic:str=MQTT.TOPIC):
    """
    Publish message
    :param message: string to be sent
    :param topic: topic for message
    """
    state = micro_task(tag=f"mqtt.publish.{topic}", task=_publish(message, topic))
    state = "starting" if state else "already running"
    return f"Message send, {state}"


def subscribe(topic:str=None, commands:str=None, raw_dict:dict|None=None):
    """
    Subscribe for single topics and set callback function(s) aka command(s)
    :param topic: topic string, ex.: 'lights'
    :param commands: semicolon separated commands. ex.: 'rgb toggle; cct toggle'
    OR
    :param raw_dict: python dict string for multi topic subscription, ex.: {"lights": ["rgb toggle", "cct toggle"], ...}

    return: all or selected topics command
    """
    updated = False
    topic = topic.strip()
    # Register single topic
    if topic and commands:
        # raw commands structure: 'rgb toggle; cct toggle'
        commands = [ c.strip() for c in commands.split(";") ]
        # commands: Topic LUT structure: {'topic': ['mod func'], ..., 'lights': ['rgb toggle', 'cct toggle']}
        updated = True if MQTT.TOPIC_COMMAND_LUT.get(topic, None) is None else False
        MQTT.TOPIC_COMMAND_LUT[topic] = commands
    # Register multiple topics at once
    elif isinstance(raw_dict, dict):
        updated = True
        MQTT.TOPIC_COMMAND_LUT.update(raw_dict)
    # Start subscribe task
    if updated:
        state = micro_task(tag="mqtt.subscribe", task=_subscribe())
        state = "starting" if state else "already running"
        return f"Subscribe, {state}"

    # Return handling
    if topic is not None:
        # Return selected topic commands
        return MQTT.TOPIC_COMMAND_LUT.get(topic, None)
    # Return registered topics
    return MQTT.TOPIC_COMMAND_LUT


def _configure(server_ip:str, username:str, password:str):
    # Define configuration
    config["keepalive"] = 120
    config["queue_len"] = 1  # Use event interface with default queue
    # Define configuration
    config['client_id'] = cfgget("devfid")
    config['ssid'] = cfgget("staessid")
    config['wifi_pw'] = cfgget("stapwd")
    config['port'] = 1883                       # expose????
    config['server'] = server_ip                # '172.20.10.2'
    config['user'] = username                   # test
    config['password'] = password               # '12345'
    return config


def load(server_ip:str, username:str, password:str, topic:str=None, commands:str=None, raw_dict:dict|None=None):
    """
    Load MQTT_AS receiver...
    :param server_ip: server IP address
    :param username: server user
    :param password: server user password

    :param topic: topic string, ex.: 'lights'
    :param commands: semicolon separated commands. ex.: 'rgb toggle; cct toggle'
    OR
    :param raw_dict: python dict string for multi topic subscription, ex.: {"lights": ["rgb toggle", "cct toggle"], ...}
    """
    MQTTClient.DEBUG = True
    MQTT.CLIENT = MQTTClient(_configure(server_ip, username, password))

    state = micro_task(tag="mqtt.client", task=_init_client(topic, commands, raw_dict))
    return "Starting" if state else "Already running"


def help():
    return ("load <server_ip> <username> <password> topic='micros', commands='rgb toggle; cct toggle'",
            "subscribe topic='micros', commands='rgb toggle; cct toggle'",
            "subscribe #without params dumps the topic-command data structure",
            "publish message='hello' topic='micros'",
            "HINT: task show mqtt.*")
