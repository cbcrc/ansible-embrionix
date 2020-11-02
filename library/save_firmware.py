#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
import sys, yaml, json, os
from module_utils.flatdict import FlatDict

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

def get_firmware_version(firmware):
    firmware = firmware.split(' ')
    return firmware[-1]

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=False),
            hostname=dict(type='str', required=False),
            firmware_version=dict(type='str', required=False),
            serial_number=dict(type='str', required=False),
            low_level=dict(type='dict', required=False, default={}),
            low_level_ip=dict(type='dict', required=False, default={}),
            group_name=dict(type='list', required=True)
        ),
        supports_check_mode=True,
    )
    
    filename = "reports/firmware.json"
    if(os.path.exists(filename)):        
        with open(filename, 'r') as f:
            firmware_json_data = f.read()
        f.close()
        firmware_json = json.loads(firmware_json_data)
    else:
        firmware_json = {}
        with open(filename, "w") as f:
            json.dump(firmware_json, f, indent=2)
            f.close()
               
    if('arista' in module.params['group_name']):
        if(module.params['low_level'] == {}):
            low_level = module.params['low_level_ip']
        elif (module.params['low_level_ip'] == {}):
            low_level = module.params['low_level']
        else:
            low_level = "Not Found"  
        f.close()
        for device in low_level:
            if(device not in firmware_json.keys()):
                firmware_json[device] = {}
            firmware_json[device]['hostname'] = device
            firmware_json[device]['ip'] = low_level[device][0]
            firmware_json[device]['low_level'] = low_level[device][1]

        with open(filename, "w") as f:
            json.dump(firmware_json, f, indent=2)
    if('emsfp' in module.params['group_name']):
        try:          
            with open("reports/__test.txt", "a") as test:
                test.write(str(module.params['hostname']))  
                test.write("\n")
            high_level = str(module.params['firmware_version'])
            if(module.params['hostname'] not in firmware_json):
                firmware_json[module.params['hostname']] = {}
            firmware_json[module.params['hostname']]['hostname'] = module.params['hostname']
            firmware_json[module.params['hostname']]['ip'] = module.params['ip_addr']
            firmware_json[module.params['hostname']]['high_level'] = high_level
            firmware_json[module.params['hostname']]['serial_number'] = module.params['serial_number']

            with open(filename, "w") as f:
                json.dump(firmware_json, f, indent=2)
        except Exception as e:
            high_level = str(e)


    module.exit_json(changed=True, msg=f"Ok")
    
                

if __name__ == '__main__':
    main()