#!/usr/bin/env python
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
module: emsfp_ipconfig.py
author:
    - Société Radio-Canada
version_added: ""
short_description: Configure emsfp ipconfig
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
HOSTNAME_REGEX = "^[-\s\w\W]*$"

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
    # module.exit_json(changed=False, msg=f"Payload: \n{module.params}")

    url = f"http://{emsfp.EMSFP.clean_ip(module.params['ip_addr'])}/emsfp/node/v1/self/ipconfig/"

    sfp_module = emsfp.EMSFP(url, module.params, PAYLOAD_TEMPLATE)
    module_inital_config = sfp_module.get_module_config
    # module.exit_json(changed=False, msg=f"Payload: \n{sfp_module.get_payload}")
    # module.exit_json(changed=False, msg=f"Payload: \n{sfp_module.get_module_config}")
    # module.exit_json(changed=True, msg=f"get paylaod diff: \n{sfp_module.get_payload_diff}")
    # module.exit_json(changed=True,msg=f"Payload: \n{sfp_module.get_flattened_payload()}\nConfig:\n{sfp_module.get_flattened_config()}")
    # module.exit_json(changed=False, msg=f"Diff keys: \n{sfp_module.get_diff_keys}")

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