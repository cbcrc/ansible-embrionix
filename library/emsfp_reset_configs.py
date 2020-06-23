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
    'reboot': ["bool"],
    'config_reset': ["choices", "0", "flows", "application", "system"]
}
def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            reboot=dict(type='bool'),
            config_reset=dict(type='str', choices=["0", "flows", "application", "system"])
            ),
        supports_check_mode=True,
    )

    try:
        url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/self/system/"
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=e)

    payload_params = {
        'reboot': module.params['reboot'],
        'config_reset': module.params['config_reset']
    }

    em = EMSFP(url, module.params, PAYLOAD_TEMPLATE)

    configure_em_device(module, em, validate_changes=False)

if __name__ == '__main__':
    main() 