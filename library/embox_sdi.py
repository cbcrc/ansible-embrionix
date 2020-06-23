#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address,IPv4Network
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
from module_utils.utils import configure_em_device, IP_ADDRESS_REGEX, HOSTNAME_REGEX
from yaml import dump

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: emsfp_sdi
version_added: ""
short_description: Change the sdi operating bit rate.
description:
options:
  ip_addr:
    description:
      - Management ip address of the module.
    type: str
    require: true
  operating_bit_rate:
    description:
      - Set the sdi operating bit rate to integer (for 30 hz, 60 hz, etc) or fractional (for 29.97 hz, 59.94 hz, etc).
    choices: ['integer', 'fractional']
    type: str
    require: true
notes:
  - Tested on em-6-U-8-GW
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
    "configuration": {
        "operating_bit_rate":[ "choices", "fractional", "integer"]
    }
}

em_TYPE_COMPATILIBITY = {
    '24 - em3u'
}

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            operating_bit_rate=dict(type='str', required=False)
            ),
        supports_check_mode=True
    )
    # module.exit_json(changed=False, msg=f"Payload: \n{module.params}")

    payload_params = {
        "configuration": {
            "operating_bit_rate": module.params['operating_bit_rate']
        }
    }

    url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/sdi/"

    em = EMSFP(url, payload_params, PAYLOAD_TEMPLATE)
    module_inital_config = em.target_config

    configure_em_device(module, em)

if __name__ == '__main__':
    main() 