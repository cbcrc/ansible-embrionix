#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
#

from ipaddress import IPv4Address, ip_network, ip_interface, AddressValueError, NetmaskValueError
from json import dumps as json_dumps
from yaml import dump as yaml_dump
from yaml import load as yaml_load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper,  SafeDumper, safe_dump, safe_dump_all
from yaml import YAMLError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.utils import get_module_type2
import pprint
import traceback
import sys
from deepdiff import DeepDiff
from copy import deepcopy

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

def update_em_group(em_group: dict, em_dict: dict) -> dict:
    """
    Add em_list devices in em_group dictionnary

    Args:
        em_group (dict): a dict containing the emsfp['children'] part of the hostfile.
        em_list (dict): a list of dict with embrionix devices infos

    Returns:
    [dict] the updated em_group dict
    """
    for device in em_dict:
        device_items = em_dict[device]
        device_dict = {device_items['hostname']: {'ansible_host_ip': device_items['ip_addr']}}
        device_type = get_module_type2(device_items['ip_addr'])
        if device_type in em_group:
            em_group[device_type]['hosts'].update(device_dict)
        else:
            em_group[device_type] = {'hosts': device_dict}
    return em_group

def main():
    module = AnsibleModule(
        argument_spec=dict(
            inventory_path=dict(type='str', required=True),
            device_dict=dict(type='dict', required=True)
            ),
        supports_check_mode=True
    )
    inventory_path = module.params['inventory_path']
    device_dict = module.params['device_dict']

    with open(inventory_path, 'r') as hostfile:
        try:
            inventory = yaml_load(hostfile, Loader=Loader)
        except YAMLError as e:
            module.fail_json(changed=False, msg=f"Hostfile parsing error.\n Hostfile path: {module.params['inventory_path']}\nError:\n{e}")

    try:
        if 'emsfp' in inventory['all']['children']:
            em_group = inventory['all']['children']['emsfp']['children']
        else:
            raise KeyError("key 'emsfp' not in inventory")
        updated_em_group = {}
        updated_em_group = update_em_group(deepcopy(em_group), device_dict)
    except KeyError as e:
        module.fail_json(changed=False, msg=f"KeyError: key {e} not in hostfile\n Hostfile content: {inventory}")

    if em_group == updated_em_group:
        module.exit_json(
            changed=False,
            msg=f"Nothing to change!\n"
            )
    else:
        inventory['all']['children']['emsfp']['children'] = updated_em_group
        with open(inventory_path, 'w') as hostfile:
            yaml_dump(inventory, hostfile, explicit_start=True)
        module.exit_json(
            changed=True,
            msg=f"Updated inventory:\n{yaml_dump(inventory, default_flow_style=False, explicit_start=True)}\nPrevious hostfile content:\n{yaml_dump(em_group)}\nNew hostfile content:\n{yaml_dump(updated_em_group)}\n"
            )
if __name__ == '__main__':
    main()