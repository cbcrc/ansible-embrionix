#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
from module_utils.utils import configure_em_device, IP_ADDRESS_REGEX, HOSTNAME_REGEX
from yaml import dump

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
    'alias_ip': ["ip", IP_ADDRESS_REGEX],
    'alias_ip_subnet': ["ip", IP_ADDRESS_REGEX],
    'subnet_mask': ["ip", IP_ADDRESS_REGEX],
    'gateway': ["ip", IP_ADDRESS_REGEX],
    'hostname': ["regex", HOSTNAME_REGEX],
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

    url = f"http://{IPv4Address(mmodule.params['ip_addr'])}/emsfp/node/v1/self/ipconfig/"

    em = em.EMSFP(url, module.params, PAYLOAD_TEMPLATE)
    module_inital_config = em.get_module_config

    configure_em_device(module, em)

if __name__ == '__main__':
    main() 