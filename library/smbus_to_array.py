#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import *
import json, yaml

def find_addresses(smbus):
    smbus_addresses = []
    ethernet_ports = []

    #Count number of Ethernet iteration (number of module)
    number_of_module = smbus.count('Ethernet')
    port_smbus_dict = {}

    for module in range(0 ,number_of_module):
        try:
            start_address_string = smbus[smbus.find('Ethernet'):]
            address_string = start_address_string[:start_address_string.find('5.00')]
            address_list = address_string.split(' ')
            filtered_address_list = list(filter(None, address_list)) # Remove None item of the list
            smbus = start_address_string[30:]
            port_smbus_dict[int(filtered_address_list[0][8:])] = filtered_address_list[4]

        except:
            port_smbus_dict = {}
            port_smbus_dict['error'] = 'Error parsing the smbus return.'
            return port_smbus_dict        
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