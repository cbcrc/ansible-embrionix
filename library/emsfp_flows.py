#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
from module_utils.emsfp import EMSFP, NAME_REGEX, LABEL_REGEX
from module_utils.utils import configure_em_device, IP_ADDRESS_REGEX, IP_PORT_REGEX, MAC_ADDRESS_REGEX, get_module_type2
from module_utils.emsfp_firmware_base import EB22
from yaml import dump
import logging
from re import fullmatch
from sys import exc_info
# from traceback import format_exception
import traceback
from pprint import pprint
from requests import get
from ansible.module_utils.basic import AnsibleModule

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

HEXA4B_REGEX = "^([A-Za-f]|[0-9]){1,4}$"

ENCAP_VIDEO_PAYLOAD_TEMPLATE = {
    'label': ["regex", LABEL_REGEX],
    'name': ["regex", NAME_REGEX],
    'network': {
        'src_ip_addr': ["ip"],
        'src_udp_port': ["range", 0, 65535],
        'dst_ip_addr': ["ip"],
        'dst_udp_port': ["range", 0, 65535],
        'dst_mac': ["regex", MAC_ADDRESS_REGEX],
        'vlan_tag': ["range", 0, 4096],
        # 'ssrc': ["range", 0, 4294967296], #read only value
        'enable': ["bool"],
        'rtp_pt': ["range", 0, 127],
        'dscp': ["range", 0, 63]
        }
    }

ENCAP_AUDIO_PAYLOAD_TEMPLATE = {
    'label': ["regex", LABEL_REGEX],
    'name': ["regex", NAME_REGEX],
    'network': {
        'src_ip_addr': ["ip"],
        'src_udp_port': ["range", 0, 65535],
        'dst_ip_addr': ["ip"],
        'dst_udp_port': ["range", 0, 65535],
        'dst_mac': ["regex", MAC_ADDRESS_REGEX],
        'vlan_tag': ["range", 0, 4096],
        # 'ssrc': ["range", 0, 4294967296], #read only value
        'enable': ["bool"],
        'rtp_pt': ["range", 0, 127],
        'dscp': ["range", 0, 63]
    },
    'format': {
        'aud_chan_cnt': ["range", 0, 15],
        'mapping': {
            'ch0': ["str"],
            'ch1': ["str"],
            'ch2': ["str"],
            'ch3': ["str"],
            'ch4': ["str"],
            'ch5': ["str"],
            'ch6': ["str"],
            'ch7': ["str"],
            'ch8': ["str"],
            'ch9': ["str"],
            'ch10': ["str"],
            'ch11': ["str"],
            'ch12': ["str"],
            'ch13': ["str"],
            'ch14': ["str"],
            'ch15': ["str"]
            },
        'aud_ptime_idx': ["range", 0, 5]
        }
    }

ENCAP_ANCILLARY_PAYLOAD_TEMPLATE = {
    'label': ["regex", LABEL_REGEX],
    'name': ["regex", NAME_REGEX],
    'network': {
        'src_ip_addr': ["ip"],
        'src_udp_port': ["range", 0, 65535],
        'dst_ip_addr': ["ip"],
        'dst_udp_port': ["range", 0, 65535],
        'dst_mac': ["regex", MAC_ADDRESS_REGEX],
        'vlan_tag': ["range", 0, 4096],
        # 'ssrc': ["range", 0, 4294967296], #read only value
        'enable': ["bool"],
        'rtp_pt': ["range", 0, 127],
        'dscp': ["range", 0, 63]
    },
    'format': {
        'anc_flow_profile': ["range", 0, 2]
        }
    }

DECAP_VIDEO_PAYLOAD_TEMPLATE = {
    'label': ["regex", LABEL_REGEX],
    'name': ["regex", NAME_REGEX],
    'network': {
        'src_ip_addr': ["ip"],
        'src_udp_port': ["range", 0, 65535],
        'dst_ip_addr': ["ip"],
        'dst_udp_port': ["range", 0, 65535],
        'dst_mac': ["regex", MAC_ADDRESS_REGEX],
        'vlan_tag': ["range", 0, 4096],
        # 'ssrc': ["range", 0, 4294967296], #read only value
        'pkt_filter_src_ip': ["bool"],
        'pkt_filter_src_udp': ["bool"],
        'pkt_filter_src_mac': ["bool"],
        'pkt_filter_dst_ip': ["bool"],
        'pkt_filter_dst_udp': ["bool"],
        'pkt_filter_dst_mac': ["bool"],
        'pkt_filter_vlan': ["bool"],
        'pkt_filter_ssrc': ["bool"],
        'igmp_src_ip': ["ip"],
        'sender_type': ["range", 0, 2],
        'enable': ["bool"]
        }
    }

DECAP_AUDIO_PAYLOAD_TEMPLATE = {
    'label': ["regex", LABEL_REGEX],
    'name': ["regex", NAME_REGEX],
    'network': {
        'src_ip_addr': ["ip"],
        'src_udp_port': ["range", 0, 65535],
        'dst_ip_addr': ["ip"],
        'dst_udp_port': ["range", 0, 65535],
        'dst_mac': ["regex", MAC_ADDRESS_REGEX],
        'vlan_tag': ["range", 0, 4096],
        # 'ssrc': ["range", 0, 4294967296], #read only value
        'pkt_filter_src_ip': ["bool"],
        'pkt_filter_src_udp': ["bool"],
        'pkt_filter_src_mac': ["bool"],
        'pkt_filter_dst_ip': ["bool"],
        'pkt_filter_dst_udp': ["bool"],
        'pkt_filter_dst_mac': ["bool"],
        'pkt_filter_vlan': ["bool"],
        'pkt_filter_ssrc': ["bool"],
        'igmp_src_ip': ["ip"],
        'sender_type': ["range", 0, 2],
        'enable': ["bool"]
    },
    'format': {
        'aud_chan_cnt': ["range", 0, 15],
        'mapping': {
            'ch0': ["str"],
            'ch1': ["str"],
            'ch2': ["str"],
            'ch3': ["str"],
            'ch4': ["str"],
            'ch5': ["str"],
            'ch6': ["str"],
            'ch7': ["str"],
            'ch8': ["str"],
            'ch9': ["str"],
            'ch10': ["str"],
            'ch11': ["str"],
            'ch12': ["str"],
            'ch13': ["str"],
            'ch14': ["str"],
            'ch15': ["str"]
            }
        }
    }

DECAP_ANCILLARY_PAYLOAD_TEMPLATE = {
    'label': ["regex", LABEL_REGEX],
    'name': ["regex", NAME_REGEX],
    'network': {
        'src_ip_addr': ["ip"],
        'src_udp_port': ["range", 0, 65535],
        'dst_ip_addr': ["ip"],
        'dst_udp_port': ["range", 0, 65535],
        'dst_mac': ["regex", MAC_ADDRESS_REGEX],
        'vlan_tag': ["range", 0, 4096],
        # 'ssrc': ["range", 0, 4294967296], #read only value
        'pkt_filter_src_ip': ["bool"],
        'pkt_filter_src_udp': ["bool"],
        'pkt_filter_src_mac': ["bool"],
        'pkt_filter_dst_ip': ["bool"],
        'pkt_filter_dst_udp': ["bool"],
        'pkt_filter_dst_mac': ["bool"],
        'pkt_filter_vlan': ["bool"],
        'pkt_filter_ssrc': ["bool"],
        'igmp_src_ip': ["ip"],
        'rtp_pt': ["range", 0, 127],
        'sender_type': ["range", 0, 2],
        'enable': ["bool"]
        }
    }
def check_flow_network_format(url):
    json.dumps()

def main():

    FORMAT = '%(asctime)-15s - %(name)s, %(lineno)d - %(levelname)s - %(message)s'
    logging.basicConfig(filename='logs/emsfp.log', filemode='a', format=FORMAT, level=logging.INFO)
    flow_log = logging.getLogger("emsfp-flows")

    flow_log.info("------------------- Appel du module flow -------------------")
    module = AnsibleModule(
        argument_spec=dict(
            Target=dict(type=str, required=False),
            ip_addr=dict(type=str, required=True),
            FlowType=dict(type=str, required=True),
            format_type=dict(type=str, required=False),
            sfp_type=dict(type=str, required=False),
            Flow=dict(type=str, required=True),
            label=dict(type=str, required=False),
            name=dict(type=str, required=False),
            src_ip_addr=dict(type=str, required=False),
            src_udp_port=dict(type=str, required=False),
            dst_ip_addr=dict(type=str, required=False),
            dst_udp_port=dict(type=str, required=False),
            vlan_tag=dict(type=str, required=False),
            pkt_filter_src_ip=dict(type=str, required=False),
            pkt_filter_src_udp=dict(type=str, required=False),
            pkt_filter_src_mac=dict(type=str, required=False),
            pkt_filter_dst_ip=dict(type=str, required=False),
            pkt_filter_dst_udp=dict(type=str, required=False),
            pkt_filter_dst_mac=dict(type=str, required=False),
            pkt_filter_vlan=dict(type=str, required=False),
            pkt_filter_ssrc=dict(type=str, required=False),
            # ssrc=dict(type=str, required=False), #read only value
            rtp_pt=dict(type=str, required=False),
            dscp=dict(type=str, required=False),
            igmp_src_ip=dict(type=str, required=False),
            enable=dict(type=str, required=False),
            aud_chan_map=dict(type=str, required=False),
            audio_mapping_ch0=dict(type=str, required=False, default="none"),
            audio_mapping_ch1=dict(type=str, required=False, default="none"),
            audio_mapping_ch2=dict(type=str, required=False, default="none"),
            audio_mapping_ch3=dict(type=str, required=False, default="none"),
            audio_mapping_ch4=dict(type=str, required=False, default="none"),
            audio_mapping_ch5=dict(type=str, required=False, default="none"),
            audio_mapping_ch6=dict(type=str, required=False, default="none"),
            audio_mapping_ch7=dict(type=str, required=False, default="none"),
            audio_mapping_ch8=dict(type=str, required=False, default="none"),
            audio_mapping_ch9=dict(type=str, required=False, default="none"),
            audio_mapping_ch10=dict(type=str, required=False, default="none"),
            audio_mapping_ch11=dict(type=str, required=False, default="none"),
            audio_mapping_ch12=dict(type=str, required=False, default="none"),
            audio_mapping_ch13=dict(type=str, required=False, default="none"),
            audio_mapping_ch14=dict(type=str, required=False, default="none"),
            audio_mapping_ch15=dict(type=str, required=False, default="none"),
            aud_ptime_idx=dict(type=str, required=False),
            aud_chan_cnt=dict(type=str, required=False, default="none"),
            anc_flow_profile=dict(type=str, required=False),
            sender_type=dict(type=str, required=False)
        ),
        supports_check_mode=True,
    )

    if module.params['ip_addr'] != 'None':
        ip_addr = str(IPv4Address(module.params['ip_addr']))
    elif module.params['Target'] != 'None':
        ip_addr = str(IPv4Address(module.params['Target']))
    else:
        module.fail_json(changed=False, msg=f"Missing parameter: ip_addr or Target must be provided")

    #Clean IPs of unused 0
    if module.params['src_ip_addr']:
        module.params['src_ip_addr'] = str(IPv4Address(module.params['src_ip_addr']))
    if module.params['dst_ip_addr']:
        module.params['dst_ip_addr'] = str(IPv4Address(module.params['dst_ip_addr']))

    # Validate the mendatory keys (Target, Flow and FlowType).
    for mendatory_key in ['Flow', 'FlowType']:
        if (module.params[mendatory_key] == "") or (module.params[mendatory_key] == None):
            module.fail_json(changed=False,  msg=f"Mendatory key {mendatory_key} was not provided.", module_ip=ip_addr, module_flow_id=module.params['Flow'])

    #Generate dest multicast mac
    if module.params['dst_ip_addr'] != "":
        match = fullmatch(IP_ADDRESS_REGEX, module.params['dst_ip_addr'])
        if match:
            list_ip_byte = module.params['dst_ip_addr'].split('.')
            byte1 = hex(int(list_ip_byte[1])&0b01111111)[2:].zfill(2)
            byte2 = hex(int(list_ip_byte[2]))[2:].zfill(2)
            byte3 = hex(int(list_ip_byte[3]))[2:].zfill(2)
            module.params['dst_mac'] = "01:00:5e:%s:%s:%s" % (byte1, byte2, byte3)
        else:
            module.fail_json(changed=False, msg=f"ERROR - The value assign to the IP of the device {ip_addr} of the flow {module.params['Flow']} is not valid : {module.params['dst_ip_addr']}")
    else :
        module.params['dst_mac'] = ""

    # Padding 4Bytes to specific attributes and convert to lowcap
    flow_payload = {}
    for field in module.params :
        flow_payload[field] = module.params[field]
    
    ListAttributes4B =['aud_chan_map']
    for x in ListAttributes4B :
        if (x in flow_payload.keys()) and (flow_payload[x] != '') and (flow_payload[x] is not None):
                temp_value = flow_payload[x].lower()
                flow_payload[x] = temp_value.rjust(4, '0')

    module_type = get_module_type2(ip_addr)

    try:
        url = f"http://{ip_addr}/emsfp/node/v1/flows/{module.params['Flow']}"
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=f"{e}\n")

    # Get firmware version
    mf = em = EB22(ip_addr)
    firmware_version = float(em.getActiveFirmawareVersion())

    # Set flag to indicate if flow network section is a list or not
    em = EMSFP()
    em.url = url
    try:
        em.download_target_config()
    except Exception as e:
        module.fail_json(changed=False, msg=f"Error while trying to retreive target configuration\nurl: {url}\nerror message:\n{e}\n")
    target_config = em.target_config
    if target_config != {}:
        try:
            flow_network_is_list = isinstance(target_config['network'], list)
        except KeyError as e:
            module.fail_json(changed=False, msg=f"KeyError while trying to determine if network is unique or list\nDevice ip: {ip_addr}\nerror message:\n{e}\n")
    else:
        module.fail_json(changed=False, msg=f"The retreived flow parameters are empty. The specified flow may not exist.\nurl: {url}\n")


    # module.exit_json(changed=False, msg=f"FlowType: {module.params['FlowType']}\nformat_type: {module.params['format_type']}\nsfp_type: {module.params['sfp_type']}\nenable: {module.params['enable']}\n", default_flow_style=False)
    payload_params = {}
    selected_payload_template = "None"
    try:
        if module.params['FlowType'] == "enc_video" or (
            module.params['format_type'] == "video" and (
                (module_type in ["Embox6_8", "box3u_25G"] and module.params['Flow'][:2] in ["10", "30", "50", "70"]) or 
                (module_type in ["st2110_10G_enc"] and module.params['Flow'][1:3] in ["04", "05"])
            )
        ):
            PAYLOAD_TEMPLATE = ENCAP_VIDEO_PAYLOAD_TEMPLATE
            selected_payload_template = "ENCAP_VIDEO_PAYLOAD_TEMPLATE"
            payload_params = {
                'label': module.params['label'],
                'name': module.params['name'],
                'network': {
                    'src_ip_addr': module.params['src_ip_addr'],
                    'src_udp_port': module.params['src_udp_port'],
                    'dst_ip_addr': module.params['dst_ip_addr'],
                    'dst_udp_port': module.params['dst_udp_port'],
                    'dst_mac': module.params['dst_mac'],
                    'vlan_tag': module.params['vlan_tag'],
                    'rtp_pt': module.params['rtp_pt'],
                    'dscp': module.params['dscp'],
                    'enable': module.params['enable']
                }
            }
        elif module.params['FlowType'] == "enc_audio" or (
            module.params['format_type'] == "audio" and (
                (module_type in ["Embox6_8", "box3u_25G"] and module.params['Flow'][:2] in ["11", "12", "13", "14", "31", "32", "33", "34", "51", "52", "53", "54", "71", "72", "73", "74"]) or
                (module_type in ["st2110_10G_enc"] and module.params['Flow'][1:3] in ["14", "15", "24", "25", "34", "35", "44", "45", "54", "55", "64", "65", "74", "75", "84", "85"])
            )
        ):
            # flow_log.info(f"Création payload enc_audio")
            PAYLOAD_TEMPLATE = ENCAP_AUDIO_PAYLOAD_TEMPLATE
            selected_payload_template = "ENCAP_AUDIO_PAYLOAD_TEMPLATE"
            payload_params = {
                'label': module.params['label'],
                'name': module.params['name'],
                'network': {
                    'src_ip_addr': module.params['src_ip_addr'],
                    'src_udp_port': module.params['src_udp_port'],
                    'dst_ip_addr': module.params['dst_ip_addr'],
                    'dst_udp_port': module.params['dst_udp_port'],
                    'dst_mac': module.params['dst_mac'],
                    'vlan_tag': module.params['vlan_tag'],
                    'enable': module.params['enable'],
                },
                'format': {
                    'aud_chan_cnt': module.params['aud_chan_cnt'],
                    'aud_ptime_idx': module.params['aud_ptime_idx']
                    }
            }
            # Add a mapping section to the payload if needed
            if module.params['aud_chan_cnt'] != "" and module_type == "st2110_10G_enc" and firmware_version >= 3.5:
                if int(module.params['aud_chan_cnt']) > 0:
                    flow_log.info(f"url: {url}")
                    flow_log.info(f"aud_chan_cnt: {module.params['aud_chan_cnt']}")
                    mapping_dict = {}
                    for channel in range(int(module.params['aud_chan_cnt'])):
                        channel_nbr = str(channel)
                        mapping_value = module.params[f'audio_mapping_ch{channel_nbr}']
                        if module.params[f'audio_mapping_ch{channel_nbr}'] != "none":
                            key = f"ch{channel_nbr}"
                            value = module.params[f"audio_mapping_ch{channel_nbr}"]
                            mapping_dict.update({key: value})
                    payload_params["format"]["mapping"] = mapping_dict
            flow_log.info(f"payload_param: {payload_params}")

        elif module.params['FlowType'] == "enc_ancillary" or (
            module.params['format_type'] == "ancillary" and (
                (module_type in ["Embox6_8", "box3u_25G"] and module.params['Flow'][:2] in ["19", "39", "59", "79"]) or
                (module_type in ["st2110_10G_enc"] and module.params['Flow'][1:3] in ["94", "95"])
            )
        ):
            PAYLOAD_TEMPLATE = ENCAP_ANCILLARY_PAYLOAD_TEMPLATE
            selected_payload_template = "ENCAP_ANCILLARY_PAYLOAD_TEMPLATE"
            payload_params = {
                'label': module.params['label'],
                'name': module.params['name'],
                'network': {
                    'src_ip_addr': module.params['src_ip_addr'],
                    'src_udp_port': module.params['src_udp_port'],
                    'dst_ip_addr': module.params['dst_ip_addr'],
                    'dst_udp_port': module.params['dst_udp_port'],
                    'dst_mac': module.params['dst_mac'],
                    'vlan_tag': module.params['vlan_tag'],
                    'rtp_pt': module.params['rtp_pt'],
                    'dscp': module.params['dscp'],
                    'enable': module.params['enable']
                },
                'format': {
                    'anc_flow_profile': module.params['anc_flow_profile']
                    }
                }

        elif module.params['FlowType'] == "dec_video" or (
            module.params['format_type'] == "video" and (
                (module_type in ["Embox6_8", "box3u_25G"] and module.params['Flow'][:2] in ["20", "40", "60", "80"]) or
                (module_type in ["st2110_10G_dec"] and module.params['Flow'][1:3] in ["04", "05"])
            )
        ):
            if (module_type in ["Embox3" , "Embox6", "box3u_25G", "Embox6_8"] and flow_network_is_list is True):
                PAYLOAD_TEMPLATE = DECAP_VIDEO_PAYLOAD_TEMPLATE
                selected_payload_template = "DECAP_VIDEO_PAYLOAD_TEMPLATE_NETWORK_LIST"
                payload_params = {
                    'label': module.params['label'],
                    'name': module.params['name'],
                    'network': [{
                            'src_ip_addr': module.params['src_ip_addr'],
                            'src_udp_port': module.params['src_udp_port'],
                            'dst_ip_addr': module.params['dst_ip_addr'],
                            'dst_udp_port': module.params['dst_udp_port'],
                            'dst_mac': module.params['dst_mac'],
                            'vlan_tag': module.params['vlan_tag'],
                            'pkt_filter_src_ip': module.params['pkt_filter_src_ip'],
                            'pkt_filter_src_udp': module.params['pkt_filter_src_udp'],
                            'pkt_filter_src_mac': module.params['pkt_filter_src_mac'],
                            'pkt_filter_dst_ip': module.params['pkt_filter_dst_ip'],
                            'pkt_filter_dst_udp': module.params['pkt_filter_dst_udp'],
                            'pkt_filter_dst_mac': module.params['pkt_filter_dst_mac'],
                            'pkt_filter_vlan': module.params['pkt_filter_vlan'],
                            'pkt_filter_ssrc': module.params['pkt_filter_ssrc'],
                            'igmp_src_ip': module.params['igmp_src_ip'],
                            'sender_type': module.params['sender_type'],
                            'enable': module.params['enable']
                        }]
                    }  
            else:
                PAYLOAD_TEMPLATE = DECAP_VIDEO_PAYLOAD_TEMPLATE
                selected_payload_template = "DECAP_VIDEO_PAYLOAD_TEMPLATE"
                payload_params = {
                    'label': module.params['label'],
                    'name': module.params['name'],
                    'network': {
                        'src_ip_addr': module.params['src_ip_addr'],
                        'src_udp_port': module.params['src_udp_port'],
                        'dst_ip_addr': module.params['dst_ip_addr'],
                        'dst_udp_port': module.params['dst_udp_port'],
                        'dst_mac': module.params['dst_mac'],
                        'vlan_tag': module.params['vlan_tag'],
                        'pkt_filter_src_ip': module.params['pkt_filter_src_ip'],
                        'pkt_filter_src_udp': module.params['pkt_filter_src_udp'],
                        'pkt_filter_src_mac': module.params['pkt_filter_src_mac'],
                        'pkt_filter_dst_ip': module.params['pkt_filter_dst_ip'],
                        'pkt_filter_dst_udp': module.params['pkt_filter_dst_udp'],
                        'pkt_filter_dst_mac': module.params['pkt_filter_dst_mac'],
                        'pkt_filter_vlan': module.params['pkt_filter_vlan'],
                        'pkt_filter_ssrc': module.params['pkt_filter_ssrc'],
                        'igmp_src_ip': module.params['igmp_src_ip'],
                        'sender_type': module.params['sender_type'],
                        'enable': module.params['enable']
                        }
                    }

        elif module.params['FlowType'] == "dec_audio" or (
            module.params['format_type'] == "audio" and (
                (module_type in ["Embox6_8", "box3u_25G"] and module.params['Flow'][:2] in ["21", "22", "23", "24", "41", "42", "43", "44", "61", "62", "63", "64", "81", "82", "83", "84"]) or
                (module_type in ["st2110_10G_dec"] and module.params['Flow'][1:3] in ["14", "15", "24", "25", "34", "35", "44", "45"])
            )
        ):
            PAYLOAD_TEMPLATE = DECAP_AUDIO_PAYLOAD_TEMPLATE
            selected_payload_template = "DECAP_AUDIO_PAYLOAD_TEMPLATE"
            payload_params = {
                'label': module.params['label'],
                'name': module.params['name'],
                'network': {
                    'src_ip_addr': module.params['src_ip_addr'],
                    'src_udp_port': module.params['src_udp_port'],
                    'dst_ip_addr': module.params['dst_ip_addr'],
                    'dst_udp_port': module.params['dst_udp_port'],
                    'dst_mac': module.params['dst_mac'],
                    'vlan_tag': module.params['vlan_tag'],
                    'pkt_filter_src_ip': module.params['pkt_filter_src_ip'],
                    'pkt_filter_src_udp': module.params['pkt_filter_src_udp'],
                    'pkt_filter_src_mac': module.params['pkt_filter_src_mac'],
                    'pkt_filter_dst_ip': module.params['pkt_filter_dst_ip'],
                    'pkt_filter_dst_udp': module.params['pkt_filter_dst_udp'],
                    'pkt_filter_dst_mac': module.params['pkt_filter_dst_mac'],
                    'pkt_filter_vlan': module.params['pkt_filter_vlan'],
                    'pkt_filter_ssrc': module.params['pkt_filter_ssrc'],
                    'igmp_src_ip': module.params['igmp_src_ip'],
                    'sender_type': module.params['sender_type'],
                    'enable': module.params['enable']
                },
                'format': {
                    'aud_chan_cnt': module.params['aud_chan_cnt'],
                    }
                }
            # Add a mapping section to the payload if needed
            if module.params['aud_chan_cnt'] != "" and module_type == "st2110_10G_dec" and firmware_version >= 3.5:
                if int(module.params['aud_chan_cnt']) > 0:
                    # flow_log.info(f"url: {url}")
                    # flow_log.info(f"aud_chan_cnt: {module.params['aud_chan_cnt']}")
                    mapping_dict = {}
                    for channel in range(int(module.params['aud_chan_cnt'])):
                        channel_nbr = str(channel)
                        mapping_value = module.params[f'audio_mapping_ch{channel_nbr}']
                        if module.params[f'audio_mapping_ch{channel_nbr}'] != "none":
                            key = f"ch{channel_nbr}"
                            value = module.params[f"audio_mapping_ch{channel_nbr}"]
                            mapping_dict.update({key: value})
                    payload_params["format"]["mapping"] = mapping_dict
            # flow_log.info(f"payload_param: {payload_params}")

        elif module.params['FlowType'] == "dec_ancillary" or (
            module.params['format_type'] == "ancillary" and (
                (module_type in ["Embox6_8", "box3u_25G"] and module.params['Flow'][:2] in ["29", "49", "69", "89"]) or
                (module_type in ["st2110_10G_dec"] and module.params['Flow'][1:3] in ["94", "95"])
            )
        ):
            PAYLOAD_TEMPLATE = DECAP_ANCILLARY_PAYLOAD_TEMPLATE
            selected_payload_template = "DECAP_ANCILLARY_PAYLOAD_TEMPLATE"
            payload_params = {
                'label': module.params['label'],
                'name': module.params['name'],
                'network': {
                    'src_ip_addr': module.params['src_ip_addr'],
                    'src_udp_port': module.params['src_udp_port'],
                    'dst_ip_addr': module.params['dst_ip_addr'],
                    'dst_udp_port': module.params['dst_udp_port'],
                    'dst_mac': module.params['dst_mac'],
                    'vlan_tag': module.params['vlan_tag'],
                    'pkt_filter_src_ip': module.params['pkt_filter_src_ip'],
                    'pkt_filter_src_udp': module.params['pkt_filter_src_udp'],
                    'pkt_filter_src_mac': module.params['pkt_filter_src_mac'],
                    'pkt_filter_dst_ip': module.params['pkt_filter_dst_ip'],
                    'pkt_filter_dst_udp': module.params['pkt_filter_dst_udp'],
                    'pkt_filter_dst_mac': module.params['pkt_filter_dst_mac'],
                    'pkt_filter_vlan': module.params['pkt_filter_vlan'],
                    'pkt_filter_ssrc': module.params['pkt_filter_ssrc'],
                    'igmp_src_ip': module.params['igmp_src_ip'],
                    'rtp_pt': module.params['rtp_pt'],
                    'sender_type': module.params['enable'],
                    'enable': module.params['enable']
                    }
                }
        else:
            module.fail_json(changed=False, msg=f"Error: Conditions not met for payload_params creation.\n" \
            f"Device type: {module_type}\n" \
            f"Flow type: {module.params['FlowType']}\n" \
            f"format_type: {module.params['format_type']}\n" \
            f"Flow id[:2]: {module.params['Flow'][:2]}\n" \
            f"Flow id[1:3]: {module.params['Flow'][1:3]}\n" \
            f"Network is list? {flow_network_is_list}\n")
    except Exception as e:
        exc_type, exc_value, exc_tb = exc_info()
        module.fail_json(changed=False, msg=f"Error during payload_param creation.\n" \
        f"Device type: {module.params['sfp_type']}\n" \
        f"Network is list? {flow_network_is_list}\n" \
        f"Error: {e}\n" \
        f"Traceback:{pprint(traceback.format_exception(exc_type, exc_value, exc_tb))}")

    # module.exit_json(changed=False, msg=f"FlowType: {module.params['FlowType']}\nformat_type: {module.params['format_type']}\nsfp_type: {module.params['sfp_type']}\nenable: {module.params['enable']}\npayload_params:\n{payload_params}\n", default_flow_style=False)
    # module.exit_json(changed=False, msg=f"payload_params:\n{payload_params}\n", default_flow_style=True)

    try:
        em = EMSFP(url, payload_params, PAYLOAD_TEMPLATE)
    except Exception as e:
        exc_type, exc_value, exc_tb = exc_info()
        module.fail_json(changed=False, msg=f"Flow type: {module_type}\nSelected template: {selected_payload_template}\n" \
        f"Network is list? {flow_network_is_list}\n" \
        f"Error: {e}\n" \
        f"Traceback:{pprint(traceback.format_exception(exc_type, exc_value, exc_tb))}")
        # f"Traceback:{pprint(traceback.print_exc(10))}")
    configure_em_device(module, em,  message=f"Device type: {module_type}\nSelected template: {selected_payload_template}\nRoute: {url}\nPayload: {em.payload}\n")
        # f"Selected template: {selected_payload_template}\n" \
        # f"Route: {url}\nPayload: {em.payload}\n")
if __name__ == '__main__':
    main() 