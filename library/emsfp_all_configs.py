#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import emsfp_firmware_base
from ansible.module_utils import emsfp
from requests import get
from requests import put
from yaml import dump
import json
import sys

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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            mode=dict(type='str', choices=["download", "upload"], required=True),
            config=dict(type='dict', required=False)
            ),
        supports_check_mode=True,
    )

    base_url = f"http://{emsfp.EMSFP.clean_ip(module.params['ip_addr'])}/emsfp/node/v1"    

    # Initiating the upload firmware object.
    emsfp_firmware = emsfp_firmware_base.EB22(module.params['ip_addr'])

    # Get module device type and set the firmware path base on the type of module.
    module_type = emsfp_firmware.getModuleType()

    # Initiating the emsfp object.
    emsfp_module = emsfp.EMSFP()

    #Define the API config routes proper to all module type
    regular_config_list = [
        {'config_name': 'ipconfig', 'config_url': f"{base_url}/self/ipconfig/"},
        {'config_name': 'ptp', 'config_url': f"{base_url}/refclk/"},
    ]
    id_separated_config_list = [
        {'config_name': 'flows', 'config_url': f"{base_url}/flows/"}
    ]
    parameter_id_separated_config_list = [
        {'config_name': 'ptp', 'config_url': f"{base_url}/refclk/", 'parameter_id': 'uuid'}
    ]

    if module_type == 'Encapsulator':
        id_separated_config_list.append({'config_name': 'sdi_input', 'config_url': f"{base_url}/sdi_input/"})
    elif module_type == 'Decapsulator':
        id_separated_config_list.append({'config_name': 'sdi_audio', 'config_url': f"{base_url}/sdi_audio/"})
        id_separated_config_list.append({'config_name': 'sdi_output', 'config_url': f"{base_url}/sdi_output/"})


    def get_sfp_module_config(url):
        emsfp_module.url = url
        try:
            response = emsfp_module.get_target_config()
        except Exception as e:
            module.fail_json(changed=False, msg=f"{e}")
        return response

    def send_sfp_module_config(url, payload):
        emsfp_module.url = url
        emsfp_module.payload = payload                   
        try:
            response = emsfp_module.send_downloaded_configuration()
        except Exception as e:
            module.fail_json(changed=False, msg=f"{e}")
        return response

    if module.params['mode'] == 'download':
        # Create the initial dict that will be use to create the yaml file.
        module_dict = {'emsfp_module': {}}
        module_dict['emsfp_module'] = {'module_ip': module.params['ip_addr']}
        module_dict['emsfp_module']['parameter'] = {}

        # Gather configuration for regular config route.
        for regular_config in regular_config_list:
            response = get_sfp_module_config(regular_config['config_url'])
            module_dict['emsfp_module']['parameter'][regular_config['config_name']] = response

        # Gather configuration for id based config route.
        for id_separated_config in id_separated_config_list:           
            id_list = get_sfp_module_config(id_separated_config['config_url'])
            if id_list != {'msg': "value can't be parsed to json."}:
                module_dict['emsfp_module']['parameter'][id_separated_config['config_name']] = {}
                for id in id_list:
                    response = get_sfp_module_config(id_separated_config['config_url'] + id)
                    module_dict['emsfp_module']['parameter'][id_separated_config['config_name']][id[:-1]] = response

        # Gather configuration for parameter id based config route.
        for parameter_id_separated_config in parameter_id_separated_config_list:           
            module_parent_parameter = get_sfp_module_config(parameter_id_separated_config['config_url'])
            for module_parameter in module_parent_parameter.keys():
                if module_parameter == parameter_id_separated_config['parameter_id']:
                    module_dict['emsfp_module']['parameter'][parameter_id_separated_config['config_name']+"-"+parameter_id_separated_config['parameter_id']] = {}
                    for id in module_parent_parameter[module_parameter]:
                        response = get_sfp_module_config(parameter_id_separated_config['config_url'] + id)
                        module_dict['emsfp_module']['parameter'][parameter_id_separated_config['config_name']+"-"+parameter_id_separated_config['parameter_id']][id] = response
 
        module.exit_json(changed=False, msg=f"{dump(module_dict, default_flow_style=False)}")

    elif module.params['mode'] == 'upload':
        if module.check_mode == False:
            response_list = []
            response_key_only_in_payload_to_send_list = []
            response_key_only_in_target_module_list = []
            for module_config_name, module_config_value in module.params['config']['parameter'].items():
                # Send configuration for the regular config route.
                for config in regular_config_list:
                    if module_config_name in config['config_name']:                  
                        response = send_sfp_module_config(url=config['config_url'], payload=module_config_value)
                        response_list.append(f"Configuration Section: {module_config_name} Payload sent!")
                        if response['key_only_in_target_module_list'] != []:
                            response_key_only_in_payload_to_send_list.append(f"Configuration Section: {module_config_name} - {str(response['key_only_in_target_module_list'])} ")
                        if response['key_only_in_payload_to_send_list'] != []:
                            response_key_only_in_target_module_list.append(f"Configuration Section: {module_config_name} - {str(response['key_only_in_payload_to_send_list'])} ")

                # Send configuration for the id based config route.
                for config in id_separated_config_list:
                    if module_config_name in config['config_name']:
                        for id, id_config in module_config_value.items():
                            response = send_sfp_module_config(url=config['config_url'] + id, payload=id_config)
                            response_list.append(f"Configuration Section: {module_config_name} ID: {id} Payload sent!")
                            if response['key_only_in_target_module_list'] != []:
                                response_key_only_in_payload_to_send_list.append(f"Configuration Section: {module_config_name} ID: {id} - {str(response['key_only_in_target_module_list'])} ")
                            if response['key_only_in_payload_to_send_list'] != []:
                                response_key_only_in_target_module_list.append(f"Configuration Section: {module_config_name} ID: {id} - {str(response['key_only_in_payload_to_send_list'])} ")

                # Send configuration for the id based config route.
                for config in parameter_id_separated_config_list:
                    if module_config_name == config['config_name'] + "-" + config['parameter_id']:
                        for id, id_config in module_config_value.items():
                            response = send_sfp_module_config(url=config['config_url'] + id, payload=id_config)
                            response_list.append(f"Configuration Section: {config['config_name']} Parameter: {config['parameter_id']} ID: {id} Payload sent!")
                            if response['key_only_in_target_module_list'] != []:
                                response_key_only_in_payload_to_send_list.append(f"Configuration Section: {config['config_name']} Parameter: {config['parameter_id']} ID: {id} - {str(response['key_only_in_target_module_list'])} ")
                            if response['key_only_in_payload_to_send_list'] != []:
                                response_key_only_in_target_module_list.append(f"Configuration Section: {config['config_name']} Parameter: {config['parameter_id']} ID: {id} - {str(response['key_only_in_payload_to_send_list'])} ")


        # Exit module differently base on different situation.
        if (module.check_mode == True):
            module.exit_json(changed=True, msg=f"Payload would had been sent to {module.params['ip_addr']} (check_mode)")
        else:
            module.exit_json(changed=True, msg=response_list, warning_config_only_in_payload_to_send=response_key_only_in_payload_to_send_list, warning_config_only_in_target_module=response_key_only_in_target_module_list)

if __name__ == '__main__':
    main()