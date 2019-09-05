#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from module_utils import emsfp
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
# Verifie que les valeurs entrées sont de 0.0.0.0 à 255.255.255.255.
IP_ADDRESS_REGEX = "^(([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))$"
DUMMY_REGEX = "^[-\s\w\W]*$"

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

    url = f"http://{emsfp.EMSFP.clean_ip(module.params['ip_addr'])}/emsfp/node/v1/self/system/"

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
                    response_message = sfp_module.send_configuration(validate_changes=False)
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