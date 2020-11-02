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
from logging.handlers import RotatingFileHandler
from re import fullmatch
from sys import exc_info
import traceback
from pprint import pprint
from requests import get, RequestException
from ansible.module_utils.basic import AnsibleModule

log_format = '%(asctime)-15s - %(name)s, %(lineno)d - %(levelname)s - %(message)s'
logging.basicConfig(filename='logs/flows.log', filemode='a', format=log_format, level=logging.INFO)
flow_log = logging.getLogger('emsfp_flows')
handler = RotatingFileHandler('logs/flows.log', maxBytes=512, backupCount=1)
flow_log.addHandler(handler)

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

log_format = logging.Formatter('%(asctime)-15s - %(name)s, %(lineno)d - %(levelname)s - %(message)s')
flow_log = logging.getLogger("flow")
handler = logging.FileHandler('logs/flows.log', 'a')
handler.setFormatter(log_format)
handler.setLevel(logging.INFO)
flow_log.addHandler(handler)

HEXA4B_REGEX = "^([A-Za-f]|[0-9]){1,4}$"

def get_flow_type(url: str) -> str:
    """
    get_flow_type connect to Embrionix device and return the flows type.

    Args:
        url (str): Route to the module api

    Raises:
        e: [Exception] RequestException

    Returns:
        [str]: The flow type
    """
    try:
        response = get(url)
        response_dict = response.json()
    except RequestException as e:
        raise e

    flow_type = "unknown"
    if response_dict['format']['format_type'] == 'video':
        if 'jumbo_frame' in response_dict:
            flow_type = 'em_enc_video'
        elif 'cdis' in response_dict:
            flow_type = 'em_dec_cdis_video'
        elif 'format_code_format' in response_dict['format']:
            if 'sampling_format' in response_dict['format']:
                flow_type = 'embox_dec_video'
            else:
                flow_type = 'emsfp_dec_video'

    if response_dict['format']['format_type'] == 'audio':
        if 'aud_chan_cnt' in response_dict['format'] and 'aud_chan_map' not in response_dict['format']:
            flow_type = 'em_audio_chan_cnt'
        elif 'aud_chan_cnt' not in response_dict['format'] and 'aud_chan_map' in response_dict['format']:
            flow_type = 'em_audio_chan_map'

    if response_dict['format']['format_type'] == 'ancillary':
        if 'anc_flow_profile' in response_dict['format']:
            flow_type = 'em_enc_ancillary'
        else:
            flow_type = 'em_dec_ancillary'
    # flow_log.info(f"flow_type: {flow_type}")
    return flow_type

def get_flow_payload(flow_type: str, params: str, firmware_version: float) -> dict:
    """
    get_flow_payload returns the payload to configure the flow.

    Args:
        flow_type (str): The flow type.
        params (str): The parameters given to Ansible module
        firmware_version (float): The Embrionix device firmware version

    Returns:
        dict: the flow payload
    """
    payload = {}
    if flow_type == 'em_dec_ancillary':
        payload = get_em_dec_ancillary_payload(params)
    elif flow_type == 'em_enc_ancillary':
        payload = get_em_enc_ancillary_payload(params)
    elif flow_type == 'em_audio_chan_cnt':
        payload = get_em_audio_chan_cnt_payload(params, firmware_version)
    elif flow_type == 'em_audio_chan_map':
        payload = get_em_audio_chan_map_payload(params)
    elif flow_type == 'em_enc_video':
        payload = get_em_enc_video_payload(params)
    elif flow_type == 'em_dec_cdis_video':
        payload = get_em_dec_cdis_video_payload(params)
    elif flow_type == 'embox_dec_video':
        payload = get_embox_dec_video_payload(params)
    elif flow_type == 'emsfp_dec_video':
        payload = get_emsfp_dec_video_payload(params)
    flow_log.info(f"params:\n{params}")
    flow_log.info(f"payload:\n{payload}")
    return payload

def get_basic_payload(params: dict) -> dict:
    basic_payload = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'rtp_pt': params['rtp_pt'],
            'enable': params['enable']
            }
        }
    return basic_payload

def get_em_dec_ancillary_payload(params: dict) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'pkt_filter_src_ip': params['pkt_filter_src_ip'],
            'pkt_filter_src_udp': params['pkt_filter_src_udp'],
            'pkt_filter_src_mac': params['pkt_filter_src_mac'],
            'pkt_filter_dst_ip': params['pkt_filter_dst_ip'],
            'pkt_filter_dst_udp': params['pkt_filter_dst_udp'],
            'pkt_filter_dst_mac': params['pkt_filter_dst_mac'],
            'pkt_filter_vlan': params['pkt_filter_vlan'],
            'pkt_filter_ssrc': params['pkt_filter_ssrc'],
            'igmp_src_ip': params['igmp_src_ip'],
            'rtp_pt': params['rtp_pt'],
            'sender_type': params['enable'],
            'enable': params['enable']
            }
        }
    return payload_params

def get_em_enc_ancillary_payload(params: dict) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'rtp_pt': params['rtp_pt'],
            'dscp': params['dscp'],
            'enable': params['enable']
        },
        'format': {
            'anc_flow_profile': params['anc_flow_profile']
            }
        }
    return payload_params

def get_em_audio_chan_cnt_payload(params: dict, firmware_version: float) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'enable': params['enable'],
        },
        'format': {
            'aud_chan_cnt': params['aud_chan_cnt'],
            'aud_ptime_idx': params['aud_ptime_idx']
            }
    }
    # Add a mapping section to the payload if needed
    if params['aud_chan_cnt'] != "" and firmware_version >= 3.5:
        if int(params['aud_chan_cnt']) > 0:
            mapping_dict = {}
            for channel in range(int(params['aud_chan_cnt'])):
                channel_nbr = str(channel)
                mapping_value = params[f'audio_mapping_ch{channel_nbr}']
                if params[f'audio_mapping_ch{channel_nbr}'] != "none":
                    key = f"ch{channel_nbr}"
                    value = params[f"audio_mapping_ch{channel_nbr}"]
                    mapping_dict.update({key: value})
            payload_params["format"]["mapping"] = mapping_dict
    return payload_params

def get_em_audio_chan_map_payload(params: dict) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'rtp_pt': params['rtp_pt'],
            'dscp': params['dscp'],
            'enable': params['enable']
        },
        'format': {
            'aud_chan_map': params['aud_chan_map'],
            }
        }
    return payload_params 

def get_em_enc_video_payload(params: dict) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'rtp_pt': params['rtp_pt'],
            'dscp': params['dscp'],
            'enable': params['enable']
        }
    }
    return payload_params

def get_em_dec_cdis_video_payload(params: dict) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': [
            {
                'src_ip_addr': params['src_ip_addr'],
                'src_udp_port': params['src_udp_port'],
                'dst_ip_addr': params['dst_ip_addr'],
                'dst_udp_port': params['dst_udp_port'],
                'dst_mac': params['dst_mac'],
                'vlan_tag': params['vlan_tag'],
                'pkt_filter_src_ip': params['pkt_filter_src_ip'],
                'pkt_filter_src_udp': params['pkt_filter_src_udp'],
                'pkt_filter_src_mac': params['pkt_filter_src_mac'],
                'pkt_filter_dst_ip': params['pkt_filter_dst_ip'],
                'pkt_filter_dst_udp': params['pkt_filter_dst_udp'],
                'pkt_filter_dst_mac': params['pkt_filter_dst_mac'],
                'pkt_filter_vlan': params['pkt_filter_vlan'],
                'pkt_filter_ssrc': params['pkt_filter_ssrc'],
                'igmp_src_ip': params['igmp_src_ip'],
                'sender_type': params['sender_type'],
                'enable': params['enable']
            }
        ]
    }
    return payload_params

def get_embox_dec_video_payload(params: dict) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'pkt_filter_src_ip': params['pkt_filter_src_ip'],
            'pkt_filter_src_udp': params['pkt_filter_src_udp'],
            'pkt_filter_src_mac': params['pkt_filter_src_mac'],
            'pkt_filter_dst_ip': params['pkt_filter_dst_ip'],
            'pkt_filter_dst_udp': params['pkt_filter_dst_udp'],
            'pkt_filter_dst_mac': params['pkt_filter_dst_mac'],
            'pkt_filter_vlan': params['pkt_filter_vlan'],
            'pkt_filter_ssrc': params['pkt_filter_ssrc'],
            'igmp_src_ip': params['igmp_src_ip'],
            'sender_type': params['sender_type'],
            'enable': params['enable']
            }
        }
    return payload_params

def get_emsfp_dec_video_payload(params: dict) -> dict:
    payload_params = {
        'label': params['label'],
        'name': params['name'],
        'network': {
            'src_ip_addr': params['src_ip_addr'],
            'src_udp_port': params['src_udp_port'],
            'dst_ip_addr': params['dst_ip_addr'],
            'dst_udp_port': params['dst_udp_port'],
            'dst_mac': params['dst_mac'],
            'vlan_tag': params['vlan_tag'],
            'pkt_filter_src_ip': params['pkt_filter_src_ip'],
            'pkt_filter_src_udp': params['pkt_filter_src_udp'],
            'pkt_filter_src_mac': params['pkt_filter_src_mac'],
            'pkt_filter_dst_ip': params['pkt_filter_dst_ip'],
            'pkt_filter_dst_udp': params['pkt_filter_dst_udp'],
            'pkt_filter_dst_mac': params['pkt_filter_dst_mac'],
            'pkt_filter_vlan': params['pkt_filter_vlan'],
            'pkt_filter_ssrc': params['pkt_filter_ssrc'],
            'igmp_src_ip': params['igmp_src_ip'],
            'sender_type': params['sender_type'],
            'enable': params['enable']
            }
        }
    return payload_params

def generate_dest_multicast_mac(ip: str) -> str:
    """
    generate_dest_multicast_mac generate multicast mac for provided ip.

    Args:
        ip (str): ip to generate multicast from

    Raises:
        TypeError: when ip address isn't valid

    Returns:
        str: the multicast mac
    """
    dest_mac = ""
    if ip != "":
        match = fullmatch(IP_ADDRESS_REGEX, ip)
        if match:
            list_ip_byte = ip.split('.')
            byte1 = hex(int(list_ip_byte[1])&0b01111111)[2:].zfill(2)
            byte2 = hex(int(list_ip_byte[2]))[2:].zfill(2)
            byte3 = hex(int(list_ip_byte[3]))[2:].zfill(2)
            dest_mac = "01:00:5e:%s:%s:%s" % (byte1, byte2, byte3)
        else:
            e_msg = f"Provided ip addess \'{ip}\' is invalid."
            raise TypeError(e_msg)
    return dest_mac

def main():
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

    #Generate dest multicast mac
    try:
        module.params['dst_mac'] = generate_dest_multicast_mac(module.params['dst_ip_addr'])
    except TypeError as e:
        module.fail_json(changed=False,  msg=f"Error generating multicast mac: {e}", module_ip=ip_addr, module_flow_id=module.params['Flow'])

    try:
        url = f"http://{ip_addr}/emsfp/node/v1/flows/{module.params['Flow']}"
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=f"{e}\n")

    payload_params = {}
    selected_payload_template = "None"
    try:
        # Get firmware version
        ef = EB22(ip_addr)
        module_type = get_flow_type(url)
        payload_params = get_flow_payload(module_type, module.params, float(ef.getActiveFirmawareVersion()))
    except Exception as e:
        exc_type, exc_value, exc_tb = exc_info()
        module.fail_json(changed=False, msg=f"Error during payload_param creation.\n" \
        f"Device type: {module.params['sfp_type']}\n" \
        f"Error: {e}\n" \
        f"Traceback:{pprint(traceback.format_exception(exc_type, exc_value, exc_tb))}")

    try:
        em = EMSFP(url, payload_params)
    except Exception as e:
        exc_type, exc_value, exc_tb = exc_info()
        module.fail_json(changed=False, msg=f"Flow type: {module_type}\nSelected template: {selected_payload_template}\n" \
        f"Error: {e}\n" \
        f"Traceback:{pprint(traceback.format_exception(exc_type, exc_value, exc_tb))}")
    configure_em_device(
        module,
        em,
        message=f"Device type: {module_type}\nSelected template: {selected_payload_template}\nRoute: {url}\nPayload: {em.payload}\n")
if __name__ == '__main__':
    main() 