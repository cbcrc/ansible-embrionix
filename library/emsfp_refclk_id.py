#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address,IPv4Network
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
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
            dscp=dict(type='str')
            ),
            supports_check_mode=True, 
        )

    payload_params = {
    "domain_num": module.params['domain_num'],
    "vlan_id": module.params['vlan_id'],
    "dscp": module.params['dscp']
    }

    if not fullmatch(REF_CLOCK_ID, module.params['reference_clock_id']):
        error_msg = f"reference_clock_id \'{module.params['reference_clock_id']}\' est invalide selon le regex: {REF_CLOCK_ID}"
        module.fail_json(changed=False, msg=error_msg)

    url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/refclk/{module.params['reference_clock_id']}/"

    em = EMSFP(url, payload_params, PAYLOAD_TEMPLATE)
    module_inital_config = em.target_config

    configure_em_device(module, em)

if __name__ == '__main__':
    main() 