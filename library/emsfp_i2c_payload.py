#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import *

def port_build_dict(smbus_addresses, port_number, source_payload_dict):
    try:
        payload_dict = {}
        if len(port_number) == 3:
            payload_dict = {'smbus_address': smbus_addresses[port_number[1:]]}
        elif len(port_number) == 2:
            payload_dict = {'smbus_address': smbus_addresses[port_number]}
        elif len(port_number) == 1:
            payload_dict = {'smbus_address': smbus_addresses[port_number]}
        for key, value in source_payload_dict.items():
            separated_bytes_list = value.split(' ')
            payload_dict[key + '_' + "first"] = separated_bytes_list[0]
            payload_dict[key + '_' + "second"] = separated_bytes_list[1]
            payload_dict[key + '_' + "third"] = separated_bytes_list[2]
            payload_dict[key + '_' + "fourth"] = separated_bytes_list[3]

    except:
        payload_dict = {}
        payload_dict['error'] = 'Error creating the payload.'
        return payload_dict   
    return payload_dict

def mac_build_dict(mac_smbus_correspondance, mac_address, source_payload_dict):
    payload_dict = {}
    for single_correspondance in mac_smbus_correspondance:
        if single_correspondance['mac_address'] == mac_address.replace(':', ' '):
            try:
                payload_dict = {'smbus_address': single_correspondance['smbus_address']}
                for key, value in source_payload_dict.items():
                    separated_bytes_list = value.split(' ')
                    payload_dict[key + '_' + "first"] = separated_bytes_list[0]
                    payload_dict[key + '_' + "second"] = separated_bytes_list[1]
                    payload_dict[key + '_' + "third"] = separated_bytes_list[2]
                    payload_dict[key + '_' + "fourth"] = separated_bytes_list[3]
            except:
                payload_dict = {}
                payload_dict['error'] = 'Error creating the payload.'
                return payload_dict
            return payload_dict
    if payload_dict == {}:
        payload_dict['error'] = 'MAC Adress not found.'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            mac_smbus_correspondance=dict(type='list', required=True),
            mac_address=dict(type='str', required=True),
            smbus_addresses=dict(type='dict', required=True),
            port_number=dict(type='str', required=True),
            ip_addr=dict(type='str', required=True),
            subnet_mask=dict(type='str', required=True),
            gateway=dict(type='str', required=True)
            ),
        supports_check_mode=True,
    )

    source_payload_dict = {
        'ip': module.params['ip_addr'],
        'subnet_mask': module.params['subnet_mask'],
        'gateway': module.params['gateway']
    }

    if module.params['mac_smbus_correspondance'] == [] :
        converted_dict = port_build_dict(module.params['smbus_addresses'], module.params['port_number'], source_payload_dict )
        if 'error' in converted_dict:
            module.fail_json(changed=False, msg=f"{converted_dict['error']} module ip : {module.params['ip_addr']}.")
        module.exit_json(changed=False, msg=converted_dict)
    else:
        converted_dict = mac_build_dict(module.params['mac_smbus_correspondance'], module.params['mac_address'], source_payload_dict)
        if 'error' in converted_dict:
            module.fail_json(changed=False, msg=f"{converted_dict['error']} - MAC Address : {module.params['mac_address']}.")
        module.exit_json(changed=False, msg=converted_dict)


if __name__ == '__main__':
    main()