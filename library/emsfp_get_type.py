#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import *
from ansible.module_utils import emsfp_firmware_base

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
    *** Part of this code whas provided by the company Embrionix.
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
    ip_addr = module.params['ip_addr']

    emsfp_firmware = emsfp_firmware_base.EB22(ip_addr)
    emsfp_firmware.getModuleType()
    module.exit_json(changed=False, msg=f"Module type: {emsfp_firmware.moduleType}", type=emsfp_firmware.moduleType)

if __name__ == "__main__":
    main()