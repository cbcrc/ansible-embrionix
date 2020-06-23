#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address,IPv4Network
from ansible.module_utils.basic import AnsibleModule

from yaml import dump


def check_ips(compare_dict):
    msg = ""
    for key, value in compare_dict.items():
        #Clean Network adresses before comparaison
        module = IPv4Address(value['module'])
        expected = IPv4Address(value['expected'])

        #Compare network adresses
        if module != expected:
            msg += f" The network address {key} on the module is different from what's expected."
    return msg


def main():
    module = AnsibleModule(
        argument_spec=dict(
            read_ip_addr=dict(type='str', required=True),
            read_subnet_mask=dict(type='str', required=True),
            read_gateway=dict(type='str', required=True),
            expected_ip_addr=dict(type='str', required=True),
            expected_subnet_mask=dict(type='str', required=True),
            expected_gateway=dict(type='str', required=True)
            ),
        supports_check_mode=True,
    )

    compare_dict = { 
        'ip_addr': {'module': module.params['read_ip_addr'], 'expected': module.params['expected_ip_addr']},
        'subnet_mask': {'module': module.params['read_subnet_mask'],'expected': module.params['expected_subnet_mask']}, 
        'gateway': {'module': module.params['read_gateway'], 'expected': module.params['expected_gateway']}
        }

    response = check_ips(compare_dict)

    if response == "":
        module.exit_json(changed=False, msg=f"The module is configured as expected.", compared_value=dump(compare_dict, default_flow_style=False))
    else:
        module.fail_json(changed=False, msg=response, compared_value=dump(compare_dict, default_flow_style=False))

if __name__ == '__main__':
    main()