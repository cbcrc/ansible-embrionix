#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
import json, yaml

def remove_redundant_spaces(intput_string):
    output_string = ''
    last_space = False
    for c in intput_string:
        if c == ' ':
            last_space = True
        else:
            if last_space:
                output_string = output_string + ' '
            output_string = output_string + c
            last_space = False
    return output_string

def find_addresses(smbus):

    line_list = []
    smbus_devices = []
    ethernet_ports = []
    port_smbus_dict = {}

    for line in smbus.splitlines():
        temp_line = remove_redundant_spaces(line)
        line_list = temp_line.split(' ')
        if line_list[0].startswith('Ethernet'):
            ethernet_ports.append(line_list)
        elif line_list[0].startswith('SmbusDevice') and line_list[3] == '5.00':
            smbus_devices.append(line_list)
    
    for device in smbus_devices:
        for port in ethernet_ports:
            if device[1][:5] == port[1][:5]:
                port_smbus_dict.update({port[0].strip('Ethernet'): device[1]})
    return port_smbus_dict

def main():
    module = AnsibleModule(
        argument_spec=dict(
            smbus=dict(type='str', required=True)
            ),
        supports_check_mode=True,
    )

    port_smbus_dict = find_addresses(module.params['smbus'])

    if 'error' in port_smbus_dict:
        module.fail_json(changed=False, msg=f"Error Parsing the smbus response : {module.params['smbus']}")
    module.exit_json(changed=False, msg=port_smbus_dict)


if __name__ == '__main__':
    main()