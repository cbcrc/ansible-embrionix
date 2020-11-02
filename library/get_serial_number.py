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
        serial_number = em.getSerialNumber()
    except Exception as e:
        module.exit_json(changed=False, msg=f"Error while trying to obtain serial number.\n Exception message: {e}", serial_number="Failed to connect")
    
    module.exit_json(changed=False, msg=f"Serial Number: {serial_number}", serial_number=serial_number)

if __name__ == "__main__":
    main()