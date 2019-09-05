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
# Verifie que les valeurs entrées sont de 0.0.0.0 à 255.255.255.255.
IP_ADDRESS_REGEX = "^(([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))$"
SDI_CHANNEL_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}:[0-7]:[0-1]$"
SDI_CHANNEL_ID_REGEX = "^b[0-1][0-9a-f]{6}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

PAYLOAD_TEMPLATE = {
    "sdi_aud_chans_cfg": {
        "ch0": ["regex", SDI_CHANNEL_REGEX],
        "ch1": ["regex", SDI_CHANNEL_REGEX],
        "ch2": ["regex", SDI_CHANNEL_REGEX],
        "ch3": ["regex", SDI_CHANNEL_REGEX],
        "ch4": ["regex", SDI_CHANNEL_REGEX],
        "ch5": ["regex", SDI_CHANNEL_REGEX],
        "ch6": ["regex", SDI_CHANNEL_REGEX],
        "ch7": ["regex", SDI_CHANNEL_REGEX],
        "ch8": ["regex", SDI_CHANNEL_REGEX],
        "ch9": ["regex", SDI_CHANNEL_REGEX],
        "ch10": ["regex", SDI_CHANNEL_REGEX],
        "ch11": ["regex", SDI_CHANNEL_REGEX],
        "ch12": ["regex", SDI_CHANNEL_REGEX],
        "ch13": ["regex", SDI_CHANNEL_REGEX],
        "ch14": ["regex", SDI_CHANNEL_REGEX],
        "ch15": ["regex", SDI_CHANNEL_REGEX]
        }
    }

def main():
    arguments = dict(sdi_audio_configs_payload=dict(type='dict', required=True))
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            sdi_channel_id=dict(type='str', required=True),
            ch0=dict(type='str'),
            ch1=dict(type='str'),
            ch2=dict(type='str'),
            ch3=dict(type='str'),
            ch4=dict(type='str'),
            ch5=dict(type='str'),
            ch6=dict(type='str'),
            ch7=dict(type='str'),
            ch8=dict(type='str'),
            ch9=dict(type='str'),
            ch10=dict(type='str'),
            ch11=dict(type='str'),
            ch12=dict(type='str'),
            ch13=dict(type='str'),
            ch14=dict(type='str'),
            ch15=dict(type='str')
            ),
            supports_check_mode=True, 
        )
    # module.exit_json(changed=False, msg=f"Payload: \n{module.params}")

    if not fullmatch(SDI_CHANNEL_ID_REGEX, module.params['sdi_channel_id']):
        error_msg = f"sdi_channel_id \'{module.params['sdi_channel_id']}\' est invalide selon le regex: {SDI_CHANNEL_ID_REGEX}"
        module.fail_json(changed=False, msg=error_msg)

    url = f"http://{emsfp.EMSFP.clean_ip(module.params['ip_addr'])}/emsfp/node/v1/sdi_output/{module.params['sdi_channel_id']}/"

    emsfp_module = emsfp.EMSFP(url, module.params, PAYLOAD_TEMPLATE)
    module_inital_config = emsfp_module.get_module_config
    # module.exit_json(changed=False, msg=f"Payload: \n{emsfp_module.get_payload}")
    # module.exit_json(changed=False, msg=f"diff_item_keys: \n{emsfp_module.get_diff_item_keys}")
    # module.exit_json(changed=False, msg=f"Payload: \n{emsfp_module.get_trimmed_payload()}")
    # module.exit_json(changed=False, msg=f"Payload: \n{emsfp_module.get_module_config}")
    # module.exit_json(changed=True, msg=f"get paylaod diff: \n{emsfp_module.get_payload_diff}")
    # module.exit_json(changed=True,msg=f"Payload: \n{emsfp_module.get_flattened_payload()}\nConfig:\n{emsfp_module.get_flattened_config()}")
    # module.exit_json(changed=False, msg=f"Diff keys: \n{emsfp_module.get_diff_keys}")

    # Pousser la nouvelle config si elle est différente de la config du module
    try:
        inital_comp = emsfp_module.get_config_diff
        # module.exit_json(changed=True, msg=f"inital_comp: {inital_comp}")
    except KeyError as e:
        module.fail_json(changed=False, msg=f"{e}")
    else:
        if inital_comp:
            if not module.check_mode:
                try:
                    response_message = emsfp_module.send_configuration()
                except Exception as e:
                    module.fail_json(changed=False, msg=f"{e}")
                else:
                    module.exit_json(changed=True, msg=f"{response_message}")
            else:
                module.exit_json(changed=True, msg=f"Values that would be modified (check_mode):", values=dump(inital_comp, default_flow_style=False))
        # Le payload == response, pas besoin d'en faire plus
        else:
            module.exit_json(changed=False, msg=f"Nothing to change: \n{dump(module_inital_config, default_flow_style=False)}")

if __name__ == '__main__':
    main() 