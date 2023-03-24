import copy
import json
import logging
import os
import sys
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Configuration constants
LOG_LEVEL = 'LOG_LEVEL'
MQTT_HOST = 'MQTT_HOST'
MQTT_PASSWORD = 'MQTT_PASSWORD'
MQTT_PORT = 'MQTT_PORT'
MQTT_SSL = 'MQTT_SSL'
MQTT_USER = 'MQTT_USER'
TYDOM_ALARM_HOME_ZONE = 'TYDOM_ALARM_HOME_ZONE'
TYDOM_ALARM_NIGHT_ZONE = 'TYDOM_ALARM_NIGHT_ZONE'
TYDOM_ALARM_PIN = 'TYDOM_ALARM_PIN'
TYDOM_IP = 'TYDOM_IP'
TYDOM_MAC = 'TYDOM_MAC'
TYDOM_PASSWORD = 'TYDOM_PASSWORD'


@dataclass
class Configuration:
    log_level = str
    mqtt_host = str
    mqtt_password = str
    mqtt_port = int
    mqtt_ssl = bool
    mqtt_user = str
    tydom_alarm_home_zone = int
    tydom_alarm_night_zone = int
    tydom_alarm_pin = str
    tydom_ip = str
    tydom_mac = str
    tydom_password = str

    def __init__(self):
        self.log_level = os.getenv(LOG_LEVEL, 'INFO').upper()
        self.mqtt_host = os.getenv(MQTT_HOST, 'localhost')
        self.mqtt_password = os.getenv(MQTT_PASSWORD, None)
        self.mqtt_port = os.getenv(MQTT_PORT, 1883)
        self.mqtt_ssl = os.getenv(MQTT_SSL, False)
        self.mqtt_user = os.getenv(MQTT_USER, None)
        self.tydom_alarm_home_zone = os.getenv(TYDOM_ALARM_HOME_ZONE, 1)
        self.tydom_alarm_night_zone = os.getenv(TYDOM_ALARM_NIGHT_ZONE, 2)
        self.tydom_alarm_pin = os.getenv(TYDOM_ALARM_PIN, None)
        self.tydom_ip = os.getenv(TYDOM_IP, 'mediation.tydom.com')
        self.tydom_mac = os.getenv(TYDOM_MAC, None)
        self.tydom_password = os.getenv(TYDOM_PASSWORD, None)

    @staticmethod
    def load():
        configuration = Configuration()
        configuration.override_configuration_for_hassio()
        configuration.validate()
        return configuration

    def override_configuration_for_hassio(self):
        hassio_options_file_path = '/data/options.json'
        try:
            with open(hassio_options_file_path) as f:
                logger.info(
                    'Hassio environment detected: loading configuration from /data/options.json')
                try:
                    data = json.load(f)
                    logger.debug('Hassio configuration parsed (%s)', data)

                    if LOG_LEVEL in data and data[LOG_LEVEL] != '':
                        self.log_level = data[LOG_LEVEL].upper()

                    if TYDOM_MAC in data and data[TYDOM_MAC] != '':
                        self.tydom_mac = data[TYDOM_MAC]

                    if TYDOM_IP in data and data[TYDOM_IP] != '':
                        self.tydom_ip = data[TYDOM_IP]

                    if TYDOM_PASSWORD in data and data[TYDOM_PASSWORD] != '':
                        self.tydom_password = data[TYDOM_PASSWORD]

                    if TYDOM_ALARM_PIN in data and data[TYDOM_ALARM_PIN] != '':
                        self.tydom_alarm_pin = str(data[TYDOM_ALARM_PIN])

                    if TYDOM_ALARM_HOME_ZONE in data and data[TYDOM_ALARM_HOME_ZONE] != '':
                        self.tydom_alarm_home_zone = data[TYDOM_ALARM_HOME_ZONE]

                    if TYDOM_ALARM_NIGHT_ZONE in data and data[TYDOM_ALARM_NIGHT_ZONE] != '':
                        self.tydom_alarm_night_zone = data[TYDOM_ALARM_NIGHT_ZONE]

                    if MQTT_HOST in data and data[MQTT_HOST] != '':
                        self.mqtt_host = data[MQTT_HOST]

                    if MQTT_USER in data and data[MQTT_USER] != '':
                        self.mqtt_user = data[MQTT_USER]

                    if MQTT_PASSWORD in data and data[MQTT_PASSWORD] != '':
                        self.mqtt_password = data[MQTT_PASSWORD]

                    if MQTT_PORT in data and data[MQTT_PORT] != '':
                        self.mqtt_port = data[MQTT_PORT]

                    if MQTT_SSL in data and data[MQTT_SSL] != '':
                        self.mqtt_ssl = data[MQTT_SSL]

                except Exception as e:
                    logger.error('Parsing error %s', e)

        except FileNotFoundError:
            logger.debug('Hassio environment not detected')

    def validate(self):
        configuration_to_print = copy.copy(self)

        # Mask sensitive values before logging
        configuration_to_print.tydom_password = Configuration.mask_value(configuration_to_print.tydom_password)
        configuration_to_print.mqtt_password = Configuration.mask_value(configuration_to_print.mqtt_password)
        configuration_to_print.tydom_alarm_pin = Configuration.mask_value(configuration_to_print.tydom_alarm_pin)

        logger.info('Validating configuration (%s', configuration_to_print.to_json())

        if self.tydom_mac is None or self.tydom_mac == '':
            logger.error('Tydom MAC address must be defined')
            sys.exit(1)

        if self.tydom_password is None or self.tydom_password == '':
            logger.error('Tydom password must be defined')
            sys.exit(1)

        logger.info('The configuration is valid')

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def mask_value(value, nb=1, char='*'):
        if value is None or value == '':
            return ''

        if len(value) < 2 * nb:
            return char * len(value)

        return f'{value[0:nb]}{char * (max(0, len(value) - (nb * 2)))}{value[len(value) - nb:len(value)]}'
