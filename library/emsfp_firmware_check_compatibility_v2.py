#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp_firmware_base import EB22
# from module_utils.utils import get_module_type2

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
            module_type=dict(default=0, type=str),
            firmware_path=dict(default=0, type=str)
        ),
        supports_check_mode=True,
    )

    module_type = module.params['module_type']
    firmware_path = module.params['firmware_path']
    if module_type == "st2110_10G_enc":
        if not ("ENC" in firmware_path):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'ENC'.")
    elif module_type == "st2110_10G_dec":
        if not ("DEC" in firmware_path):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'DEC'.")
    elif module_type == "box3u_25G":
        if not ("BOX3" in firmware_path):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'BOX3'.")
    elif module_type == "Embox6_8":
        if not ("BOX6" in firmware_path):
            module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'BOX6'.")
    else:
        module.fail_json(changed=False, msg=f"Error! Your module type was detected as '{module_type}' but the firmware name doesn't contain 'BOX6'.")

    # #  check if the file is accessible.
    if not os.path.isfile(firmware_path):
        module.fail_json(changed=False, msg="The firmware file is not accessible.", module_type=module_type)
    else:
        module.exit_json(changed=False, msg="The firmware file is accessible.", module_type=module_type, module_firmware_filepath=firmware_path)

if __name__ == "__main__":
    main()