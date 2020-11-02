#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from requests import get
from ipaddress import IPv4Address, ip_network, ip_interface, AddressValueError, NetmaskValueError
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
from module_utils.utils import configure_em_device, IP_ADDRESS_REGEX, HOSTNAME_REGEX,get_module_type
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

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            port_id=dict(type='str', required=True),
            host_pinout=dict(type='str', required=True)
            ),
        supports_check_mode=True
    )

    try:
        em_type = get_module_type(f"{IPv4Address(module.params['ip_addr'])}")
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=e)

    payload_params = {
        'host_pinout': module.params['host_pinout']
    }

    if (em_type == 'Embox6' and int(module.params['port_id']) <= 6) or (em_type == 'Embox3' and int(module.params['port_id']) <= 3):
        url = f"http://{module.params['ip_addr']}/emsfp/node/v1/port/{module.params['port_id']}"
        em = EMSFP(url, payload_params)
        configure_em_device(module, em, wait_for_device_reboot=25)
    else:
        module.fail_json(changed=False, msg=f"Port {module.params['port_id']} doesn't exists on {em_type}.")

if __name__ == '__main__':
    main()