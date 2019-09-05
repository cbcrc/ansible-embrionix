#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from module_utils import emsfp
from yaml import dump
from re import fullmatch

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

REF_CLOCK_ID = "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

PAYLOAD_TEMPLATE = {
    "domain_num": ["range", 0, 999],
    "vlan_id": ["range", 0, 9999],
    "dscp": ["range", 0, 99]
    }

def main():
    arguments = dict(sdi_audio_configs_payload=dict(type='dict', required=True))
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            reference_clock_id=dict(type='str', required=True),
            domain_num=dict(type='str'),
            vlan_id=dict(type='str'),
            dscp=dict(type='str'),
            ),
            supports_check_mode=True, 
        )

    if not fullmatch(REF_CLOCK_ID, module.params['reference_clock_id']):
        error_msg = f"reference_clock_id \'{module.params['reference_clock_id']}\' est invalide selon le regex: {REF_CLOCK_ID}"
        module.fail_json(changed=False, msg=error_msg)

    url = f"http://{emsfp.EMSFP.clean_ip(module.params['ip_addr'])}/emsfp/node/v1/refclk/{module.params['reference_clock_id']}/"

    sfp_module = emsfp.EMSFP(url, module.params, PAYLOAD_TEMPLATE)
    module_inital_config = sfp_module.get_module_config

    # Pousser la nouvelle config si elle est différente de la config du module
    try:
        inital_comp = sfp_module.get_config_diff
    except KeyError as e:
        module.fail_json(changed=False, msg=f"{e}")
    else:
        if inital_comp:
            if not module.check_mode:
                try:
                    response_message = sfp_module.send_configuration()
                except Exception as e:
                    error_msg = f"{e}, args: {e.args}"
                    module.fail_json(changed=False, msg=error_msg)
                else:
                    module.exit_json(changed=True, msg=f"{response_message}")
            else:
                module.exit_json(changed=True, msg=f"Values that would be modified (check_mode):", values=dump(inital_comp, default_flow_style=False))
        # Le payload == response, pas besoin d'en faire plus
        else:
            module.exit_json(changed=False, msg=f"Nothing to change: \n{dump(module_inital_config, default_flow_style=False)}")

if __name__ == '__main__':
    main() 