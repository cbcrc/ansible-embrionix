#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
import sys, yaml, json, os, datetime, csv
from module_utils.flatdict import FlatDict
from module_utils.utils import clean_start_time

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

def get_inventory_name(inventory):
    inventory = inventory.split("/")
    try:
        inv_i = inventory.index("inventory")
        inventory = inventory[inv_i:]
        inventory[-1] = inventory[-1].replace('\']','')
        return "_".join(inventory)
    except Exception as e:
        return "inventory"

def main():
    module = AnsibleModule(
        argument_spec=dict(
            start_time=dict(type='str', required=True),
            report_type=dict(type='str', required=True),
            
        ),
        supports_check_mode=True,
    )
    now = clean_start_time(str(module.params['start_time']))
    inventory = get_inventory_name(str(module.params['report_type']))
    
    json_file = f"reports/firmware.json"
    filename = f"reports/{now}_{inventory}_firmware_version.csv"

    with open(json_file, 'r') as f:
        firmware_json_data = f.read()
        f.close()
    
    firmware_json = json.loads(firmware_json_data)
    with open(filename, 'w') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(["Hostname", "IP_addr", "Version High Level", "Version Low Level", "Serial Number"])

        for key in firmware_json:
            if 'low_level' not in firmware_json[key].keys():
                firmware_json[key]['low_level'] = "Not Found"
            if 'high_level' not in firmware_json[key].keys():
                firmware_json[key]['high_level'] = "Not Found"
            if 'serial_number' not in firmware_json[key].keys():
                firmware_json[key]['serial_number'] = "Not Found"
            wr.writerow([key, firmware_json[key]["ip"], firmware_json[key]["high_level"], firmware_json[key]["low_level"], firmware_json[key]["serial_number"]])

        f.close()

    module.exit_json(changed=True, msg=f"Ok")
    
                

if __name__ == '__main__':
    main()