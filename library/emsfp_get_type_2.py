#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
from module_utils.emsfp import EMSFP
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.utils import get_module_type2

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
    *** Part of this code whas provided by Embrionix.
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

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True)
        ),
        supports_check_mode=True,
    )

    module_type = get_module_type2(module.params['ip_addr'])
    module.exit_json(changed=False, msg=f"Module type: {module_type}", type=module_type)

if __name__ == "__main__":
    main()