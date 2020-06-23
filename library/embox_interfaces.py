#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from yaml import dump
import json
import pprint
from ipaddress import IPv4Address, ip_network, ip_interface, AddressValueError, NetmaskValueError
from module_utils.emsfp import EMSFP
from module_utils.utils import configure_em_device
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: 
author:
    - Société Radio-Canada
version_added: ""
short_description: Courte description
description:
    - Longue description
options:

notes:

requirements:

'''

EXAMPLES = '''
'''

RETURN = '''
status:
    description:
    returned: success
    type: complex
    contains: {
        }
'''

'''[Constantes de validation des entrées]

'''

PAYLOAD_TEMPLATE = {
    'e1': {
        'static_ip': ["str"],
        'static_gateway': ["str"],
        'vlan': ["range", 0, 4096]
    },
    'e2': {
        'static_ip': ["str"],
        'static_gateway': ["str"],
        'vlan': ["range", 0, 4096]
    }
}

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            e1_ip=dict(type='str', required=False),
            e1_subnet_mask=dict(type='str', required=False),
            e1_gateway=dict(type='str', required=False),
            e1_vlan=dict(type='int', required=False,default=0),
            e2_ip=dict(type='str', required=False),
            e2_subnet_mask=dict(type='str', required=False),
            e2_gateway=dict(type='str', required=False),
            e2_vlan=dict(type='int', required=False, default=0),
            ),
        supports_check_mode=True
    )

    try:
        url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/self/interfaces/"
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=e)

    payload_params = {
        'ip_addr': module.params['ip_addr'],
        'e1': {
            'static_ip': str(ip_interface(f"{module.params['e1_ip']}/{module.params['e1_subnet_mask']}")),
            'static_gateway': str(IPv4Address(module.params['e1_gateway'])),
            'vlan': int(module.params['e1_vlan'])
        },
        'e2': {
            'static_ip': str(ip_interface(f"{module.params['e2_ip']}/{module.params['e2_subnet_mask']}")),
            'static_gateway': str(IPv4Address(module.params['e2_gateway'])),
            'vlan': int(module.params['e2_vlan'])
        }
    }

    em = EMSFP(url, payload_params, PAYLOAD_TEMPLATE)

    # message = f"Params:\n{pprint(payload_params)}\nTemplate:\n{pprint(box.payload_template)}\nTarget config:\n{pprint(box.get_module_config)}\nDiff:\n{pprint(box.get_config_diff)}"
    # message = "Params:\n{0}\nTemplate:\n{1}\nTarget config:\n{2}\nPayload values:\n{3}\nDiff:\n{4}\nPayload:\n{5}".format(
    #     dump(box.payload_params, default_flow_style=False),
    #     dump(box.payload_template, default_flow_style=False),
    #     dump(box.target_config, default_flow_style=False),
    #     dump(box.payload_values, default_flow_style=False),
    #     dump(box.get_config_diff.get_unflattened_dict(), default_flow_style=False),
    #     dump(box.payload, default_flow_style=False))

    configure_em_device(module, em, wait_for_device_reboot=25)

if __name__ == '__main__':
    main() 