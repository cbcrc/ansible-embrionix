#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp_firmware_base import EB22


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
            module_ip=dict(type=str, required=0),
            module_firmware_slot=dict(default=0, type=str)
        ),
        supports_check_mode=True,
    )

    module_ip = module.params['module_ip']
    module_firmware_slot = module.params['module_firmware_slot']

    # Checking if slot ID is in declared range.
    if module_firmware_slot not in ['0', '1', '2', '3']:
        module.fail_json(changed=False, msg="Slot must be in this range : 0,1,2 and 3.")

    # Initiating the upload firmware object.
    em = EB22(module_ip)

    # Logic to check if the selected slot can be set as Active.
    module_slot_config=em.getLoads()[module_firmware_slot]

    if bool(module_slot_config['empty']) == True:
        if module.check_mode:
            module.exit_json(changed = False, msg="CHECK_MODE_ACTIVATED : The call to set this slot as Active on the module : " +  module_ip + " in REAL mode would be skipped. The selected slot " + module_firmware_slot + " is curently empty.")
        else:
            module.exit_json(changed = False, msg="Skipping module : " +  module_ip + " The selected slot " + module_firmware_slot + " is curently empty.")
    
    if bool(module_slot_config['Active']) == True :
        if module.check_mode:
            module.exit_json(changed = True, msg="CHECK_MODE_ACTIVATED : The call to set this slot as Active on the module : " +  module_ip + " in REAL mode would be skipped. The selected slot " + module_firmware_slot + " is allready set as Active.")
        module.exit_json(changed = False, msg="Skipping module : " +  module_ip + " The selected slot " + module_firmware_slot + " is allready set as Active.")
    else:
        if module.check_mode:
            module.exit_json(changed = True, msg="CHECK_MODE_ACTIVATED : The call to set this slot as Active on the module : " +  module_ip + " in REAL mode would executed.")

    # Setting the selected slot as Active.
    response = em.setActiveSlot(module_firmware_slot)

    # Evaluate how to exit this module.
    if response[0] == False:
        module.fail_json(changed=False, msg=response[1])
    else:
        module.exit_json(changed=True, msg=response[1])


if __name__ == "__main__":
    main()