#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address,IPv4Network, AddressValueError, NetmaskValueError
from module_utils.emsfp import EMSFP
from module_utils.utils import configure_em_device
from yaml import dump
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
    'alias_ip': ["ip"],
    'alias_ip_subnet': ["ip"],
    'subnet_mask': ["ip"],
    'gateway': ["ip"],
    'hostname': ["hostname"],
    'ctl_vlan_enable': ["bool"],
    'ctl_vlan_id': ["range", 0, 4096],
    'ctl_vlan_pcp': ["range", 0, 7],
    'dhcp_enable': ["bool"],
    'port': ["range", 0, 65535]
    }

def main():
    module = AnsibleModule(
        argument_spec=dict(
            alias_ip=dict(type='str', required=False),
            alias_ip_subnet=dict(type='str', required=False),
            ip_addr=dict(type='str', required=True),
            subnet_mask=dict(type='str', required=False),
            gateway=dict(type='str', required=False),
            hostname=dict(type='str', required=False),
            port=dict(type='int', required=False),
            dhcp_enable=dict(type='bool', required=False),
            ctl_vlan_id=dict(type='int', required=False),
            ctl_vlan_pcp=dict(type='int', required=False),
            ctl_vlan_enable=dict(type='bool', required=False)
            ),
        supports_check_mode=True,
    )

    try:
        url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/self/ipconfig/"
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=e)

    payload_params = {
    'alias_ip': module.params['ip_addr'],
    'alias_ip_subnet': module.params['alias_ip_subnet'],
    'subnet_mask': module.params['subnet_mask'],
    'gateway': module.params['gateway'],
    'hostname': module.params['hostname'],
    'ctl_vlan_enable': module.params['ctl_vlan_enable'],
    'ctl_vlan_id': module.params['ctl_vlan_id'],
    'ctl_vlan_pcp': module.params['ctl_vlan_pcp'],
    'dhcp_enable': module.params['dhcp_enable'],
    'port': module.params['port'],
    }

    em = EMSFP(url, module.params, PAYLOAD_TEMPLATE)

    configure_em_device(module, em)

if __name__ == '__main__':
    main() 