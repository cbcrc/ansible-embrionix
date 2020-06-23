#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from requests import get
from ipaddress import IPv4Address,IPv4Network
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
from module_utils.utils import configure_em_device, IP_ADDRESS_REGEX, HOSTNAME_REGEX
from yaml import dump

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: emsfp_port
version_added: ""
short_description: Change the specified port's configuration.
description:
  - Set sfp_type and host_pinout parameters
options:
  ip_addr:
    description:
      - Management ip address of the module.
    type: str
    require: true
  port_id:
    description:
      - Port identifier.
    type: int
    require: true
  sfp_type:
    description:
      - Set the sfp type to either "msa" or "n-msa".
    choices: ['msa', 'n-msa']
    type: str
    require: false
  host_pinout:
    description:
      - Set the pinout type.
    choices: ['1T', '1R', '2T', '2R', 'RT']
    type: str
    require: false
notes:
  - Tested on embox-6-U-8-GW
requirements:
author:
  - Société Radio-Canada
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
    'sfp_type': ["choices", "auto", "n-msa", "msa"],
    'host_pinout': ["choices", "1T", "1R", "2R", "2T", "RT"]
    }

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            port_id=dict(type='str', required=True),
            sfp_type=dict(type='str', required=False),
            host_pinout=dict(type='str', required=False)
            ),
        supports_check_mode=True
    )

    payload_params = {
        'sfp_type': module.params['sfp_type'],
        'host_pinout': module.params['host_pinout']
        }

    em_type = get_module_type(module.params['ip_addr'])

    if module.params['port_id'] == 'all':
        ports = []
        try:
            url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/port/"
            ports = get(url)
            ports.raise_for_status()
        except Exception as e:
            module.fail_json(changed=False, msg=f"Connexion error: {e}")

        for port in ports.json():
            url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/port/"
            em = EMSFP(f"{url}{port}", payload_params, PAYLOAD_TEMPLATE)
            configure_em_device(module, em)
    elif (em_type == 'Embox6' and module.params['port_id'] <= 6) or (em_type == 'Embox3' and module.params['port_id'] <= 3):
        url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/port/{module.params['port_id']}"
        em = EMSFP(url, payload_params, PAYLOAD_TEMPLATE)
        configure_em_device(module, em)

if __name__ == '__main__':
    main()