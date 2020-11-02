#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp_firmware_base import EB22
from module_utils.utils import get_module_type

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
            module_ip=dict(type=str, required=True),
            module_enc_firmware=dict(default=0, type=str),
            module_dec_firmware=dict(default=0, type=str),
            module_box3_firmware=dict(default=0, type=str),
            module_box6_firmware=dict(default=0, type=str)
        ),
        supports_check_mode=True,
    )
    # module_ip = module.params['module_ip']
    module_enc_firmware = module.params['module_enc_firmware']
    module_dec_firmware = module.params['module_dec_firmware']
    module_box3_firmware = module.params['module_box3_firmware']
    module_box6_firmware = module.params['module_box6_firmware']

    module_type = get_module_type(module.params['ip_addr'])
    if module_type == "encap":
        module_firmware_filepath = module_enc_firmware
        if not ("ENC" in module_firmware_filepath):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'ENC'.")
    elif module_type == "decap":
        module_firmware_filepath = module_dec_firmware
        if not ("DEC" in module_firmware_filepath):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'DEC'.")
    elif module_type == "Embox3":
        module_firmware_filepath = module_Embox3_firmware
        if not ("BOX3" in module_firmware_filepath):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'BOX3'.")
    elif module_type == "Embox6":
        module_firmware_filepath = module_Embox6_firmware
        if not ("BOX6" in module_firmware_filepath):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'BOX6'.")
    else:
        module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'BOX6'.")

    # #  check if the file is accessible.
    if not os.path.isfile(module_firmware_filepath):
        module.fail_json(changed=False, msg="The firmware file is not accessible.", module_type=module_type)
    else:
        module.exit_json(changed=False, msg="The firmware file is accessible.", module_type=module_type, module_firmware_filepath=module_firmware_filepath)

if __name__ == "__main__":
    main()