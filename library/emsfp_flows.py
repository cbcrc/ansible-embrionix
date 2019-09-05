#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import *
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

# Valide si la chaîne de caractères est de longueur 16 max et contient des lettres, des chiffres, des espaces et les caractères suivant: -_
NAME_REGEX = "^[-\s\w\W]{1,25}$"
LABEL_REGEX = "^[-\s\w\W]{1,16}$"

# Vérifie que les valeurs entrées sont de 0.0.0.0 à 255.255.255.255.
IP_ADDRESS_REGEX = "^(([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))$"

# Vérifie que la valeur entrée se situe entre 0 et 65535.
IP_PORT_REGEX = "^([1-9]|[1-9][0-9]|[1-9][0-9]{2}|[1-9][0-9]{3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"

# Vérifie que la chaîne est constituée de valeurs hexadécimales espacée par un : ou un espace.
MAC_ADDRESS_REGEX = "^([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}$"

HEXA4B_REGEX = "^([A-Za-f]|[0-9]){1,4}$"

DEFAULT_PAYLOAD_TEMPLATE = {
    'aud_chan_cnt': ["range", 1, 16],
    'aud_chan_map': ["regex", HEXA4B_REGEX],
    'anc_flow_profile': ["range", 0, 2],
    'aud_ptime_idx': ["range", 0, 5],
    'dscp': ["range", 0, 63],
    'dst_ip_addr': ["ip", IP_ADDRESS_REGEX],
    'dst_mac': ["regex", MAC_ADDRESS_REGEX],
    'dst_udp_port': ["range", 0, 65535],
    'enable': ["bool"],
    'igmp_src_ip': ["ip", IP_ADDRESS_REGEX],
    'label': ["regex", LABEL_REGEX],
    'name': ["regex", NAME_REGEX],
    'pkt_filter_dst_ip': ["bool"],
    'pkt_filter_dst_mac': ["bool"],
    'pkt_filter_dst_udp': ["bool"],
    'pkt_filter_src_ip': ["bool"],
    'pkt_filter_src_mac': ["bool"],
    'pkt_filter_src_udp': ["bool"],
    'pkt_filter_ssrc': ["bool"],
    'pkt_filter_vlan': ["bool"],
    'rtp_pt': ["range", 96, 127],
    'sender_type': ["range", 0, 2],
    'src_ip_addr': ["ip", IP_ADDRESS_REGEX],
    'src_udp_port': ["range", 0, 65535],
    'ssrc': ["range", 0, 4294967296],
    'vlan_tag': ["range", 0, 4096]
    }


def main():

    module = AnsibleModule(
        argument_spec=dict(
            Target=dict(type=str, required=True),
            FlowType=dict(type=str, required=True),
            Flow=dict(type=str, required=True),
            label=dict(type=str, required=False),
            name=dict(type=str, required=False),
            src_ip_addr=dict(type=str, required=False),
            src_udp_port=dict(type=str, required=False),
            dst_ip_addr=dict(type=str, required=False),
            dst_udp_port=dict(type=str, required=False),
            dst_mac=dict(type=str, required=False),
            vlan_tag=dict(type=str, required=False),
            pkt_filter_src_ip=dict(type=str, required=False),
            pkt_filter_src_udp=dict(type=str, required=False),
            pkt_filter_src_mac=dict(type=str, required=False),
            pkt_filter_dst_ip=dict(type=str, required=False),
            pkt_filter_dst_udp=dict(type=str, required=False),
            pkt_filter_dst_mac=dict(type=str, required=False),
            pkt_filter_vlan=dict(type=str, required=False),
            pkt_filter_ssrc=dict(type=str, required=False),
            ssrc=dict(type=str, required=False),
            rtp_pt=dict(type=str, required=False),
            dscp=dict(type=str, required=False),
            igmp_src_ip=dict(type=str, required=False),
            enable=dict(type=str, required=False),
            aud_chan_map=dict(type=str, required=False),
            aud_ptime_idx=dict(type=str, required=False),
            aud_chan_cnt=dict(type=str, required=False),
            anc_flow_profile=dict(type=str, required=False),
            sender_type=dict(type=str, required=False)
        ),
        supports_check_mode=True,
    )

    # Validate the mendatory keys (Target, Flow and FlowType).
    for mendatory_key in ['Target', 'Flow', 'FlowType']:
        if (module.params[mendatory_key] == "") or (module.params[mendatory_key] == None):
            module.fail_json(changed=False,  msg=f"Mendatory key {mendatory_key} was not provided.", module_ip=module.params['Target'], module_flow_id=module.params['Flow'])

    # TODO bring the section "Padding 4bytes and set in lower" to the emsfp class.
    # Padding 4Bytes to specific attributes and convert to lowcap
    flow_payload = {}
    for field in module.params :
        flow_payload[field] = module.params[field]
    
    ListAttributes4B =['aud_chan_map']
    for x in ListAttributes4B :
        if (x in flow_payload.keys()) and (flow_payload[x] != '') and (flow_payload[x] is not None):
                temp_value = flow_payload[x].lower()
                flow_payload[x] = temp_value.rjust(4, '0')

    # Construct the PAYLOAD_TEMPLATE dict base on the PAYLOAD_LIST corresponding to the FlowType.
    if module.params['FlowType'] == "enc_video":
        FLOW_TYPE_VALID_KEY = ["label", "name", "src_ip_addr", "src_udp_port", "dst_ip_addr", "dst_udp_port", "dst_mac", "vlan_tag", "ssrc", "rtp_pt", "dscp", "enable"]
    elif module.params['FlowType'] == "enc_audio":
        FLOW_TYPE_VALID_KEY = ["label", "name", "src_ip_addr", "src_udp_port", "dst_ip_addr", "dst_udp_port", "dst_mac", "vlan_tag", "ssrc", "rtp_pt", "dscp", "enable", "aud_chan_map", "aud_ptime_idx"]
    elif module.params['FlowType'] == "enc_ancillary":
        FLOW_TYPE_VALID_KEY = ["label", "name", "src_ip_addr", "src_udp_port", "dst_ip_addr", "dst_udp_port", "dst_mac", "vlan_tag", "ssrc", "rtp_pt", "dscp", "enable", "anc_flow_profile"]
    elif module.params['FlowType'] == "dec_video":
        FLOW_TYPE_VALID_KEY = ["label", "name", "src_ip_addr", "src_udp_port", "dst_ip_addr", "dst_udp_port", "dst_mac", "vlan_tag", "pkt_filter_src_ip", "pkt_filter_src_udp", "pkt_filter_src_mac", "pkt_filter_dst_ip", "pkt_filter_dst_udp", "pkt_filter_dst_mac", "pkt_filter_vlan", "pkt_filter_ssrc", "ssrc", "igmp_src_ip", "sender_type", "enable"]
    elif module.params['FlowType'] == "dec_audio":
        FLOW_TYPE_VALID_KEY = ["label", "name", "src_ip_addr", "src_udp_port", "dst_ip_addr", "dst_udp_port", "dst_mac", "vlan_tag", "pkt_filter_src_ip", "pkt_filter_src_udp", "pkt_filter_src_mac", "pkt_filter_dst_ip", "pkt_filter_dst_udp", "pkt_filter_dst_mac", "pkt_filter_vlan", "pkt_filter_ssrc", "ssrc", "igmp_src_ip", "sender_type", "enable"]
    elif module.params['FlowType'] == "dec_ancillary":
        FLOW_TYPE_VALID_KEY = ["label", "name", "src_ip_addr", "src_udp_port", "dst_ip_addr", "dst_udp_port", "dst_mac", "vlan_tag", "pkt_filter_src_ip", "pkt_filter_src_udp", "pkt_filter_src_mac", "pkt_filter_dst_ip", "pkt_filter_dst_udp", "pkt_filter_dst_mac", "pkt_filter_vlan", "pkt_filter_ssrc", "ssrc", "igmp_src_ip", "sender_type", "enable"]

    PAYLOAD_TEMPLATE = {}
    for key in module.params.keys():
        if key in FLOW_TYPE_VALID_KEY:
            PAYLOAD_TEMPLATE[key] = DEFAULT_PAYLOAD_TEMPLATE[key]

    # Define base url for flow api route
    url = f"http://{emsfp.EMSFP.clean_ip(module.params['Target'])}/emsfp/node/v1/flows/{module.params['Flow']}"

    # Initiate the emsfp class to use general emsfp methode
    sfp_module = emsfp.EMSFP(url, flow_payload, PAYLOAD_TEMPLATE)
    
    # Get the module current configuration
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
                    response_message = sfp_module.send_configuration()
                except Exception as e:
                    module.fail_json(changed=False, msg=f"{e}")
                else:
                    module.exit_json(changed=True, msg=f"{response_message}", module_ip=module.params['Target'], module_flow_id=module.params['Flow'], module_flow_type=module.params['FlowType'])
            else:
                module.exit_json(changed=True, msg=f"Values that would be modified (check_mode):", module_ip=module.params['Target'], module_flow_id=module.params['Flow'], module_flow_type=module.params['FlowType'], values=dump(inital_comp, default_flow_style=False))
        # Le payload == response, pas besoin d'en faire plus
        else:
            module.exit_json(changed=False, msg=f"Nothing to change.", module_ip=module.params['Target'], module_flow_id=module.params['Flow'], module_flow_type=module.params['FlowType'])

if __name__ == '__main__':
    main() 