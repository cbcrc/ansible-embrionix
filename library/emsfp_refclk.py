#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address,IPv4Network
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP, REF_CLOCK_ID
from module_utils.utils import configure_em_device
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

PAYLOAD_TEMPLATE = {
    "mode": ["range", 0, 2],
    "manual_ctrl": ["bool"],
    }

def main():
    arguments = dict(sdi_audio_configs_payload=dict(type='dict', required=True))
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            mode=dict(type='str', choice=["0", "1", "2"], required=True),
            manual_ctrl=dict(type='str', required=False)
            ),
            supports_check_mode=True, 
        )

    payload_params = {
    "mode": module.params['mode'],
    "manual_ctrl": module.params['manual_ctrl']
    }

    url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/refclk/"

    em = EMSFP(url, module.params, PAYLOAD_TEMPLATE)
    module_inital_config = em.target_config

    configure_em_device(module, em)

if __name__ == '__main__':
    main() 