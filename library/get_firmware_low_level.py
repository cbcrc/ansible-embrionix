#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
import sys, yaml, json, requests, os
from requests.auth import HTTPBasicAuth
from module_utils.verify_sfp_via_sff import get_firmware

payload = {
        "jsonrpc": "2.0",
        "method": "runCmds",
        "params": {
            "format": "json",
            "timestamps": False,
            "autoComplete": False,
            "expandAliases": False,
            "cmds": [
            "show lldp neighbors"
            ],
            "version": 1
        },
        "id": "EapiExplorer-1"
    }
def get_port(port_str):
    return port_str.split("Ethernet")[-1]

def get_ips_and_ports(device_list):
    devices = []
    for device in device_list:
        obj = {}
        obj["hostname"] = device["neighborDevice"]
        obj["ip"] = device["neighborPort"]
        obj["port"] = get_port(device["port"])
        devices.append(obj)
    return devices


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            arista_user=dict(type='str', required=True),
            arista_pass=dict(type='str', required=True)
        ),
        supports_check_mode=True,
    )
    already_scanned_file = "reports/already_scanned.json"
    already_scanned = []
    if(os.path.exists(already_scanned_file)):
        with open(already_scanned_file, 'r') as f:
            already_scanned_data = f.read()
        f.close()
        already_scanned = json.loads(already_scanned_data)

    if(module.params['ip_addr'] in already_scanned):
        module.exit_json(change=False, msg=f"{module.params['ip_addr']} was already scanned", already_scanned=True)
    try:   
        res = requests.post(f"https://{module.params['ip_addr']}/command-api", verify=False, data=json.dumps(payload), auth=HTTPBasicAuth(module.params['arista_user'], module.params['arista_pass']))
        data = res.json()
        
        devices = data['result'][0]['lldpNeighbors']
        devices = get_ips_and_ports(devices)
        
        firmware_dict = {}
        ports = []
        for device in devices:
            if(device['port'].isdigit()):
                ports.append(device['port'])
        try:
            low_level = get_firmware(module.params['ip_addr'], ports, module.params['username'],  module.params['password'])
            for firmware in low_level:
                for device in devices:
                    if(device['port'].isdigit()):
                        if firmware[2] == device['port']:
                            firmware_dict[device['hostname']] = [device['ip'], firmware[1], firmware[0]]
        except Exception as e:
            firmware_dict[module.params['ip_addr']] = [module.params['ip_addr'], str(e)]
        already_scanned.append(module.params['ip_addr'])
    except Exception as e:
        already_scanned.append(module.params['ip_addr'])
        with open(already_scanned_file, "w") as f:
            json.dump(already_scanned, f)
            f.close()
        module.fail_json(changed=False, msg=f"Failed to execute with error {str(e)}", firmware={"hostname": ["Arista Switch Error", module.params['ip_addr'], str(e)  ]})
                  
    with open(already_scanned_file, "w") as f:
        json.dump(already_scanned, f)
        f.close()

    module.exit_json(changed=False, msg=f"Collected low level firmware version for arista switch {module.params['ip_addr']}", firmware=firmware_dict, already_scanned=False)
if __name__ == '__main__':
    main()