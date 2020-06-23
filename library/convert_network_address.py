#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
import json

def convert_to_dec(value):
    hex_separated_bytes_list = value.split(' ')
    dec_separated_bytes_list = []

    for separated_bytes in range(0, len(hex_separated_bytes_list)):
        dec_separated_bytes_list.append(str(int(hex_separated_bytes_list[separated_bytes], 16)))
        
    converted_value = '.'.join(dec_separated_bytes_list)
    return converted_value


def convert_to_hex(value):
    dec_separated_bytes_list = value.split('.')
    hex_separated_bytes_list = []

    for separated_bytes in range(0, len(dec_separated_bytes_list)):
        hex_separated_bytes_list.append(format(int(dec_separated_bytes_list[separated_bytes]), 'x'))
        if len(hex_separated_bytes_list[separated_bytes]) == 1:
            hex_separated_bytes_list[separated_bytes] = '0' + hex_separated_bytes_list[separated_bytes]

    converted_value = ' '.join(hex_separated_bytes_list)
    return converted_value


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            subnet_mask=dict(type='str', required=True),
            gateway=dict(type='str', required=True),
            convert_to=dict(type='str', required=True)
            ),
        supports_check_mode=True,
    )

    source_dict = {}
    converted_dict = {}
    for key, value in module.params.items():
        if key != "convert_to":
            source_dict[key] = value
            if module.params['convert_to'] == 'hex':
                converted_dict[key] = convert_to_hex(value)
            elif module.params['convert_to'] == 'dec':
                converted_dict[key] = convert_to_dec(value)

    module.exit_json(changed=False, msg={'source_value': source_dict, 'converted_value': converted_dict})

if __name__ == '__main__':
    main()