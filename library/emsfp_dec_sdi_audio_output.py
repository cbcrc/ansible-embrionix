#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address,IPv4Network, AddressValueError, NetmaskValueError
from yaml import dump
from re import fullmatch
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP, SDI_CHANNEL_REGEX, SDI_CHANNEL_ID_REGEX
from module_utils.utils import DUMMY_REGEX
from module_utils.flatdict import FlatDict
from module_utils.utils import configure_em_device

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

#Contournement pour bug avec flow ID string vide

# PAYLOAD_TEMPLATE = {
#     "sdi_aud_chans_cfg": {
#         "ch0": ["regex", SDI_CHANNEL_REGEX],
#         "ch1": ["regex", SDI_CHANNEL_REGEX],
#         "ch2": ["regex", SDI_CHANNEL_REGEX],
#         "ch3": ["regex", SDI_CHANNEL_REGEX],
#         "ch4": ["regex", SDI_CHANNEL_REGEX],
#         "ch5": ["regex", SDI_CHANNEL_REGEX],
#         "ch6": ["regex", SDI_CHANNEL_REGEX],
#         "ch7": ["regex", SDI_CHANNEL_REGEX],
#         "ch8": ["regex", SDI_CHANNEL_REGEX],
#         "ch9": ["regex", SDI_CHANNEL_REGEX],
#         "ch10": ["regex", SDI_CHANNEL_REGEX],
#         "ch11": ["regex", SDI_CHANNEL_REGEX],
#         "ch12": ["regex", SDI_CHANNEL_REGEX],
#         "ch13": ["regex", SDI_CHANNEL_REGEX],
#         "ch14": ["regex", SDI_CHANNEL_REGEX],
#         "ch15": ["regex", SDI_CHANNEL_REGEX]
#         }
#     }

PAYLOAD_TEMPLATE = {
    "sdi_aud_chans_cfg": {
        "ch0": ["regex", DUMMY_REGEX],
        "ch1": ["regex", DUMMY_REGEX],
        "ch2": ["regex", DUMMY_REGEX],
        "ch3": ["regex", DUMMY_REGEX],
        "ch4": ["regex", DUMMY_REGEX],
        "ch5": ["regex", DUMMY_REGEX],
        "ch6": ["regex", DUMMY_REGEX],
        "ch7": ["regex", DUMMY_REGEX],
        "ch8": ["regex", DUMMY_REGEX],
        "ch9": ["regex", DUMMY_REGEX],
        "ch10": ["regex", DUMMY_REGEX],
        "ch11": ["regex", DUMMY_REGEX],
        "ch12": ["regex", DUMMY_REGEX],
        "ch13": ["regex", DUMMY_REGEX],
        "ch14": ["regex", DUMMY_REGEX],
        "ch15": ["regex", DUMMY_REGEX]
        }
    }

def main():
    # arguments = dict(sdi_audio_configs_payload=dict(type='dict', required=True))
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
            supports_check_mode=True
        )
    if not fullmatch(SDI_CHANNEL_ID_REGEX, module.params['sdi_channel_id']):
        error_msg = f"sdi_channel_id \'{module.params['sdi_channel_id']}\' est invalide selon le regex: {SDI_CHANNEL_ID_REGEX}"
        module.fail_json(changed=False, msg=error_msg)

    try:
        url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/sdi_output/{module.params['sdi_channel_id']}/"
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=e)

    payload_params = {
        'sdi_aud_chans_cfg': {
            'ch0': module.params['ch0'],
            'ch1': module.params['ch1'],
            'ch2': module.params['ch2'],
            'ch3': module.params['ch3'],
            'ch4': module.params['ch4'],
            'ch5': module.params['ch5'],
            'ch6': module.params['ch6'],
            'ch7': module.params['ch7'],
            'ch8': module.params['ch8'],
            'ch9': module.params['ch9'],
            'ch10': module.params['ch10'],
            'ch11': module.params['ch11'],
            'ch12': module.params['ch12'],
            'ch13': module.params['ch13'],
            'ch14': module.params['ch14'],
            'ch15': module.params['ch15']
            }
        }

    em = EMSFP(url, payload_params, PAYLOAD_TEMPLATE)
    module_inital_config = em.target_config

    configure_em_device(module, em)

if __name__ == '__main__':
    main()