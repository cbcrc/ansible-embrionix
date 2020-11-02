#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
#
from yaml import dump as yaml_dump
from requests import get, put, RequestException
from requests.auth import HTTPBasicAuth
from json import dumps as json_dumps
from ipaddress import IPv4Address, ip_network, ip_interface, AddressValueError, NetmaskValueError
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.0.0',
    'status': ['preview'],
    'supported_by': 'community'
    }

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

def get_arp_ip_list(switch_ip: str, username: str, password: str) -> list:
    """
    Returns a list of dictionnaries containing connected device ethernet address, ip address ethernet port and age.

    Args:
        switch_ip (str): Arista switch ip address.
        username (str): User name used to connect to the Arista switch.
        password (str): Password used to connect to the Arista switch.

    Returns:
        [list]: containing a dictionnaries with the following information for all devices connected to ethernet ports:
                {
                    "hwAddress": [device ethernet address],
                    "address": [device ip address],
                    "interface": [ethernet port],
                    "age": 
                }
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "runCmds",
        "params": {
            "format": "json",
            "timestamps": "false",
            "autoComplete": "false",
            "expandAliases": "false",
            "includeErrorDetail": "false",
            "cmds": [
                "show ip arp"
            ],
            "version": "latest"
        },
        "id": "EapiExplorer-1"
    }
    try:
        response = put(f"https://{switch_ip}/command-api", auth = HTTPBasicAuth(username, password), data=json_dumps(payload), verify=False)
        return response.json()['result'][0]['ipV4Neighbors']
    except RequestException as e:
        module.fail_json(changed=False, msg=f"Connexion error: {e}")


def get_type(module_ip: str) -> str:
    """
    Returns embrionix device type.

    Args:
        module_ip (str): embrionix device ip address.

    Returns:
        [str]: the module type.
    """
    url = f"http://{module_ip}/emsfp/node/v1/self/information/"
    try:
        response = get(url).json()['type']
        return response
    except RequestException as e:
        module.fail_json(changed=False, msg=f"Error while trying to reach url \"{url}\"\nRequests module error: {e}")

def get_hostname(module_ip: str) -> str:
    """
    Returns embrionix device hostname.

    Args:
        module_ip (str): embrionix device ip address.

    Returns:
        [str]: teh module hostname.
    """
    url = f"http://{module_ip}/emsfp/node/v1/self/ipconfig/"
    try:
        response = get(url).json()['hostname']
        return response
    except RequestException as e:
        module.fail_json(changed=False, msg=f"Error while trying to reach url \"{url}\"\nRequests module error: {e}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            arista_user=dict(type='str', required=True),
            arista_pass=dict(type='str', required=True, no_log=True)
            ),
        supports_check_mode=True
    )

    try:
        ip_addr = IPv4Address(module.params['ip_addr'])
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=e)

    ip_arp_list = get_arp_ip_list(ip_addr, module.params['arista_user'], module.params['arista_pass'])

    embrionix_devices = {}
    unknown_devices = {}
    for device in ip_arp_list:
        try:
            response = get(f"http://{device['address']}/emsfp/node/v1/", timeout=1)
            if response.status_code == 200:
                embrionix_devices[f"{device['interface']}"] = {'ip_addr': device['address'], 'hostname': get_hostname(device['address']), 'type': get_type(device['address'])}
        except RequestException as e:
            unknown_devices[f"{device['interface']}"] = {'ip_addr': device['address'], 'Request error': f"{e}"}

    module.exit_json(
        changed=False,
        msg=f"Detected embrionix modules:\n{yaml_dump(embrionix_devices, default_flow_style=False)}\nUnknown devices:\n{yaml_dump(unknown_devices, default_flow_style=False)}",
        embrionix_devices=embrionix_devices,
        unknown_devices=unknown_devices
        )

if __name__ == '__main__':
    main()