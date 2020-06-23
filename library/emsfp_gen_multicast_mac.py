#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
from re import fullmatch
from module_utils.utils import IP_ADDRESS_REGEX

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
    *** Part of this code whas provided by Embrionix.
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

def get_mac_from_multicast_ip(ip):
    """Generate the multicast MAC address using the IP address
    
    Args:
        ip (string): The multicast IP address

    Returns:
        string: The MAC address

    """

    list_ip = ip.split('.')
    byte1 = hex(int(list_ip[1])&0b01111111)[2:].zfill(2)
    byte2 = hex(int(list_ip[2]))[2:].zfill(2)
    byte3 = hex(int(list_ip[3]))[2:].zfill(2)
    flow_dest_multicast_mac = "01:00:5e:%s:%s:%s" % (byte1, byte2, byte3)
    return flow_dest_multicast_mac


def main():
    module = AnsibleModule(
        argument_spec=dict(
            Target=dict(required=True, type=str),
            Flow=dict(required=True, type=str),
            dst_ip_addr=dict(required=True, type=str)
        ),
        supports_check_mode=True
    )

    Target = module.params['Target']
    Flow = module.params['Flow']
    dst_ip_addr = module.params['dst_ip_addr']

    try:
        # Verifie que les valeurs entrées sont de 0.0.0.0 à 255.255.255.255.
        if dst_ip_addr != "":
            match = fullmatch(IP_ADDRESS_REGEX, dst_ip_addr)
            if match:
                flow_dest_multicast_mac = get_mac_from_multicast_ip(dst_ip_addr)
            else:
                module.fail_json(changed=False, msg="!!! ERROR !!! The value assign to the IP of the device {} of the flow {} is not valid : {}".format(Target, Flow, dst_ip_addr))
        else :
            flow_dest_multicast_mac = ""
    except:
        module.fail_json(changed=False, msg="Error occur while generating Destination Multicast Adress for the Module : " + Target + " Flow : " + Flow)

    module.exit_json(changed=False, generated_dest_multicast_mac=flow_dest_multicast_mac)

if __name__ == '__main__':
    main()