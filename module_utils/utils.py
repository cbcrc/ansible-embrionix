#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from yaml import dump
from requests import get
from requests import RequestException

# Verifie que les valeurs entrées sont de 0.0.0.0 à 255.255.255.255.
IP_ADDRESS_REGEX = "^(([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))$"
HOSTNAME_REGEX = "^[-\s\w\W]*$"
DUMMY_REGEX = "^[-\s\w\W]*$"

# Vérifie que la valeur entrée se situe entre 0 et 65535.
IP_PORT_REGEX = "^([1-9]|[1-9][0-9]|[1-9][0-9]{2}|[1-9][0-9]{3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"

# Vérifie que la chaîne est constituée de valeurs hexadécimales espacée par un : ou un espace.
MAC_ADDRESS_REGEX = "^([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}[:\s]([a-f]|[A-F]|[0-9]){2}$"



def flatten_dict(base_dict):
    """
    flatten_dict Take a dict and flattens it.

    Args:
        base_dict: The dictionnary to flatten

    Returns:
        dict: Returns the flattened dict
    """
    flattened_dict = {}
    for key in base_dict.keys():
        if isinstance(base_dict[key], dict):
            flattened_dict.update(flatten_dict(base_dict[key]))
        else:
            flattened_dict.update({key:base_dict[key]})
    return flattened_dict



def get_diff_keys(first_dict, second_dict):
    """
    get_diff_keys Take two dicts and return a set containing the different keys between the first and second dictionnary.

    Args:
        first_dict (dict): The reference dictionnary
        second_dict (dict): The dictionnary that will be compared to the first_dictionnary
    Returns:
        set: Containing the different keys between the first and second dictionnary
    """
    first_set = set(flatten_dict(first_dict))
    return first_set.difference(set(flatten_dict(second_dict)))



def get_diff_items_keys(first_dict, second_dict):
    """
    get_diff_items_keys Create a list containing the keys for all the items having different value between the two input dictionnaries.

    Args:
        first_dict (dict): First dictionnary
        second_dict (dict): Second dictionnary
    Returns:
        list: List containing the keys for the values that are different between the two dict
    """
    diff_item_keys = []
    for key in first_dict.keys():
        if first_dict[key]:
            if key in second_dict:
                if not first_dict[key] == second_dict[key]:
                    diff_item_keys.append(key)
    return diff_item_keys



def get_module_type(ip_address):
    """
    get_module_type Get the module type to verify if the firmware correpond to the module type.

    Returns:
        [str] - [Returns module type : 'encap', 'decap', 'unknown']
    """
    get_response = get("http://" + ip_address + "/emsfp/node/v1/self/information")
    if 'Encapsulator' in get_response.json()['type'] :
        return 'encap'
    elif 'Decapsulator' in get_response.json()['type'] :
        return 'decap'
    elif 'Embox6' in get_response.json()['type']:
        return 'Embox6' 
    elif 'Embox3' in get_response.json()['type'] or 'Embox3u' in get_response.json()['type']:
        return 'Embox3'
    else:
        return 'unknown'


def get_module_type2(ip_address):
    """
    get_module_type2 Get the module type to verify if the firmware correpond to the module type.

    Returns:
        [str] - [Returns module type : 'encap', 'decap', 'unknown']
    """
    get_response = get("http://" + ip_address + "/emsfp/node/v1/self/information")
    if '3 - 2110 Encapsulator' in get_response.json()['type'] :
        return 'st2110_10G_enc'
    elif '4 - 2110 Decapsulator' in get_response.json()['type'] :
        return 'st2110_10G_dec'
    elif '22 - Embox6' in get_response.json()['type']:
        return 'Embox6_8'
    elif '24 - Embox3u' in get_response.json()['type']:
        return 'box3u_25G'
    else:
        return 'unknown'

def configure_em_device(module, emsfp_instance, validate_changes=True, message="----------------------------------------------------------------------------", wait_for_device_reboot=0):
    """
    configure_em_device Utility function to send the configuration payload. Exit the module on success or error.

    Returns:
        Args:
            module (AnsibleModule object):  Instance of AnsibleModule
            emsfp_instance (emsfp.EMSFP object): Instance of emsfp.EMSFP
            validate_changes (bool): True for configuration validation, flase otherwise.
            message (str): Optionnal debug message
    """
    wait_for_device_reboot = 0
    if validate_changes:
        wait_for_device_reboot = 15
    try:
        inital_comp = emsfp_instance.get_config_diff
    except KeyError as e:
        module.fail_json(changed=False, msg=f"Route: {emsfp_instance.url}\nPayload: {emsfp_instance.payload}\n{e}")
    else:
        if inital_comp != {}:
            if not module.check_mode:
                try:
                    response_message = emsfp_instance.send_configuration(validate_changes, wait_for_device_reboot)
                except Exception as e:
                    module.fail_json(changed=False, msg=f"Route: {emsfp_instance.url}\nDebug:\n{message}\nException occured: {e}\n----------------------------------------------------------------------------")
                else:
                    module.exit_json(changed=True, msg=f"Route: {emsfp_instance.url}\nDebug:\n{message}\n{response_message}\n----------------------------------------------------------------------------")
            else:
                module.exit_json(changed=True, msg=f"Route: {emsfp_instance.url}\nDebug:\n{message}\nValues that would be modified (check_mode):", values=dump(inital_comp, default_flow_style=False))
        # Payload == response, no need to do more
        else:
            module.exit_json(changed=False, msg=f"No changes needed!\nRoute: {emsfp_instance.url}\nDebug:\n{message}\n----------------------------------------------------------------------------")

def clean_start_time(date_string):
    date_string = date_string.split(" ")
    year = date_string[-1]
    date_string = date_string[1:4]
    date_string.append(year)
    return "_".join(date_string)
