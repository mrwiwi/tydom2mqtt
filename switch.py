import json
import time
from datetime import datetime
from sensors import sensor

#switch_position_topic = "switch/tydom/{id}/current_position"
switch_config_topic = "homeassistant/switch/tydom/{id}/config"
switch_state_topic = "sensor/tydom/{id}/state"
switch_command_topic = "switch/tydom/{id}/set_state"
switch_attributes_topic = "switch/tydom/{id}/attributes"


class Switch:
    def __init__(self, tydom_attributes, set_state=None, mqtt=None):
        self.attributes = tydom_attributes
        self.device_id = self.attributes['device_id']
        self.endpoint_id = self.attributes['endpoint_id']
        self.id = self.attributes['id']
        self.name = self.attributes['switch_name']
        try:
            self.current_state = self.attributes['state']
        except Exception as e:
            print(e)
            self.current_state = None
        #self.set_position = set_position
        self.mqtt = mqtt

    # def id(self):
    #     return self.id

    # def name(self):
    #     return self.name

    # def current_position(self):
    #     return self.current_position

    # def set_position(self):
    #     return self.set_position

    # def attributes(self):
    #     return self.attributes

    async def setup(self):
        #availability:
        #  - topic: "home/bedroom/switch1/available"

        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'Porte'
        self.device['name'] = self.name
        self.device['identifiers'] = self.id

        self.config_topic = switch_config_topic.format(id=self.id)
        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        # self.config['attributes'] = self.attributes
        self.config['command_topic'] = switch_command_topic.format(id=self.id)
        self.config['state_topic'] = switch_state_topic.format(id=self.id)
        #self.config['position_topic'] = switch_position_topic.format(id=self.id)
        self.config['json_attributes_topic'] = switch_attributes_topic.format(id=self.id)

        self.config['payload_on'] = "On"
        self.config['payload_off'] = "Off"
        self.config['state_on'] = "On"
        self.config['state_ff'] = "Off"
        #self.config['optimistic'] = 'false'
        self.config['retain'] = 'false'
        self.config['device'] = self.device
        # print(self.config)

        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_topic, json.dumps(self.config), qos=0)
        # setup_pub = '(self.config_topic, json.dumps(self.config), qos=0)'
        # return(setup_pub)

    async def update(self):
        await self.setup()

        try:
            await self.update_sensors()
        except Exception as e:
            print("Switch sensors Error :")
            print(e)


        self.state_topic = switch_state_topic.format(id=self.id, state=self.current_state)
        #self.position_topic = switch_position_topic.format(id=self.id, current_position=self.current_position)

        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.state_topic, self.current_state, qos=0, retain=True) #Switch State
            self.mqtt.mqtt_client.publish(self.config['json_attributes_topic'], self.attributes, qos=0)
        print("Switch created / updated : ", self.name, self.id, self.current_state)

        # update_pub = '(self.position_topic, self.current_position, qos=0, retain=True)'
        # return(update_pub)


    async def update_sensors(self):
        # print('test sensors !')
        for i, j in self.attributes.items():
            # sensor_name = "tydom_alarm_sensor_"+i
            # print("name "+sensor_name, "elem_name "+i, "attributes_topic_from_device ",self.config['json_attributes_topic'], "mqtt",self.mqtt)
            if not i == 'device_type' or not i == 'id':
                new_sensor = None
                new_sensor = sensor(elem_name=i, tydom_attributes_payload=self.attributes, attributes_topic_from_device=self.config['json_attributes_topic'], mqtt=self.mqtt)
                await new_sensor.update()
    # def __init__(self, name, elem_name, tydom_attributes_payload, attributes_topic_from_device, mqtt=None):


    async def put_switch_state(tydom_client, device_id, switch_id, state):
        print(switch_id, 'state', state)
        if not (state == ''):
            await tydom_client.put_devices_data(device_id, switch_id, 'state', state)
