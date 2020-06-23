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

SDI_CHANNEL_ID = "^b[0-1][0-9a-f]{6}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

PAYLOAD_TEMPLATE = {
    "line_offset": {
        "frame_sync": ["bool"],
        "offset_mode": ["bool"],
        "usec_offset": ["str"],
        "v_offset": ["str"],
        "h_offset": ["str"]
        }
    }

def main():
    arguments = dict(sdi_audio_configs_payload=dict(type='dict', required=True))
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            module_type=dict(type='str', required=True),
            sdi_channel_id=dict(type='str', required=True),
            frame_sync=dict(type='bool', required=False),
            offset_mode=dict(type='bool', required=False),
            usec_offset=dict(type='str', required=False),
            v_offset=dict(type='str', required=False),
            h_offset=dict(type='str', required=False)
            ),
            supports_check_mode=True, 
        )

    channel_type = ""
    # if module.params['module_type'] in ['encap', 'enc']:
    #     channel_type = "sdi_input"
    # elif module.params['module_type'] in ['decap', 'dec']:
    #     channel_type = "sdi_output"
    if (
        module.params['module_type'] in ['encap', 'enc', "st2110_10G_enc"]) or (
        module.params['module_type'] in ['box3u_25G', 'Embox6_8'] and module.params['sdi_channel_id'][:1] in ['b0', 'b2', 'b4', 'b6']):
        channel_type = "sdi_input"
    elif (
        module.params['module_type'] in ['decap', 'dec' "st2110_10G_dec"]) or (
        module.params['module_type'] in ['box3u_25G', 'Embox6_8'] and module.params['sdi_channel_id'][:1] in ['b1', 'b3', 'b5', 'b7']):
        channel_type = "sdi_output"
    else:
        error_msg = f"\'{module.params['module_type']}\' isn't a valid sfp module type."
        module.fail_json(changed=False, msg=error_msg)

    if not fullmatch(SDI_CHANNEL_ID, module.params['sdi_channel_id']):
        error_msg = f"sdi_channel_id \'{module.params['sdi_channel_id']}\' est invalide selon le regex: {SDI_CHANNEL_ID}"
        module.fail_json(changed=False, msg=error_msg)

    url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/{channel_type}/{module.params['sdi_channel_id']}/"

    payload_params = {
        'line_offset': {
            'frame_sync': module.params['frame_sync'],
            'offset_mode': module.params['offset_mode'],
            'usec_offset': module.params['usec_offset'],
            'v_offset': module.params['v_offset'],
            'h_offset': module.params['h_offset']
            }
        }

    em = EMSFP(url, payload_params, PAYLOAD_TEMPLATE)

    configure_em_device(module, em)

if __name__ == '__main__':
    main() 