import json
import os
import random
import shutil

import consul_config
from utils import get_logger


def _get_runtime_settings():
    try:
        shutil.copy(consul_config.RUNTIME_SETTINGS_PATH, consul_config.ORIGINAL_RUNTIME_SETTINGS_PATH)
        with open(consul_config.ORIGINAL_RUNTIME_SETTINGS_PATH) as runtime_settings_json:
            runtime_settings = json.load(runtime_settings_json)
    except:
        runtime_settings = {}

    try:
        with open(consul_config.OVERRIDE_RUNTIME_SETTINGS_PATH) as runtime_settings_json:
            runtime_settings.update(json.load(runtime_settings_json))
    except:
        pass

    ship_ips = runtime_settings.get('ships', [])
    consul_mode = consul_config.ConsulMode.BOOTSTRAP
    if runtime_settings.get('is_commander') is True:
        if ship_ips and len(ship_ips) > 0:
            consul_mode = consul_config.ConsulMode.SERVER
    if runtime_settings.get('is_commander') is False:
        consul_mode = consul_config.ConsulMode.CLIENT

    if runtime_settings.get('datacenter'):
        datacenter = runtime_settings.get('datacenter')
    else:
        datacenter = 'dc-' + str(random.randrange(1000000))

    return consul_mode, ship_ips, datacenter


def main():
    consul_mode, ship_ips, datacenter = _get_runtime_settings()
    ship_external_ip = os.environ.get('SHIP_EXTERNAL_IP', '')
    consul_config_content = consul_config.get_consul_config(consul_mode, ship_ips, datacenter, ship_external_ip)

    with open(consul_config.CONFIG_PATH, 'w') as config_file:
        config_file.write(consul_config_content)

    command = '/usr/local/bin/consul agent -config-file {config_path}'.format(config_path=consul_config.CONFIG_PATH)
    get_logger().info('RUNNING: {}'.format(command))

    args = command.split()
    os.execv(args[0], args)


if __name__ == '__main__':
    main()
