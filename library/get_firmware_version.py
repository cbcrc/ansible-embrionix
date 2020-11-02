#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp_firmware_base import EB22

from sys import exc_info
from traceback import format_exception

import yaml

def get_device_type(hostname, groups):
    skip_keys = ["all", "emsfp", "reachable_hosts", "unreachable_hosts"]
    for key in groups:
        if hostname in groups[key] and key not in skip_keys:
            return key
    return None

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            inventory=dict(type='str', required=True),
            hostname=dict(type='str', required=True),
            device_type=dict(type='dict', required=True),
        ),
        supports_check_mode=True,
    )

    module_ip = module.params['ip_addr']
    
    em = EB22(module_ip)
    try:
        firmware_version = float(em.getActiveFirmawareVersion())
    except Exception as e:
        exc_type, exc_value, exc_tb = exc_info()
        module.exit_json(changed=False, msg=f"Error while trying to obtain version.\n Exception message: {e}", version="Failed to connect")
    else:
        hostname = module.params['hostname']
        device_type = get_device_type(hostname, module.params['device_type'])

        if(device_type != None):
            with open(module.params['inventory'], 'r') as inventory_file:
                inventory = yaml.full_load(inventory_file)
            inventory['all']['children']['emsfp']['children'][device_type]['hosts'][hostname]['firmware'] = firmware_version

        with open(module.params['inventory'], 'w') as f:
            documents = yaml.dump(inventory, f)

        module.exit_json(changed=False, msg=f"Firmware version: {firmware_version}", version=firmware_version)

if __name__ == "__main__":
    main()