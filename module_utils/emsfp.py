#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from requests import get, put
from requests import exceptions as requestsExceptions
from re import fullmatch
from yaml import dump
# from module_utils.utils import clean_ip, flattened_dict
import json

# Verifie que les valeurs entrées sont de 0.0.0.0 à 255.255.255.255.
IP_ADDRESS_REGEX = "^(([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))$"



class EmbrionixError(Exception):
    pass

class InvalidPayloadItem(EmbrionixError):
    pass

class ConnexionError(EmbrionixError):
    pass

class ModuleNotConfiguredError(EmbrionixError):
    def __init__(self, message, items_not_configured={}):
        self.message = message
        self.items_not_configured = items_not_configured

class EMSFP(object):
    def __init__(self, url="", payload_items={}, payload_template={}):
        self.url = url
        self.payload_template = payload_template
        self.payload_items = self.__format_payload_items(payload_items, self.payload_template)
        self.diff_item_keys = []
        if self.url != "":
            self.target_config = self.get_target_config()
            self.payload = self.build_payload(self.payload_template)

    @staticmethod
    def clean_ip(ip_address):
        if ip_address is not "0.0.0.0":
            ip_address = ip_address.lstrip('0')
            ip_address = ip_address.replace('.0', '.')
            ip_address = ip_address.replace('..', '.0.')
        return ip_address


    @property
    def get_module_config(self):
        return self.target_config

    @property
    def url(self):
        return self.__url
    
    @url.setter
    def url(self, url):
        self.__url = url

    @property
    def payload(self):
        return self.__payload
    
    @payload.setter
    def payload(self, payload):
        self.__payload = payload

    # TODO move the call that use this methode to the method "getter" payload define just over this one.
    @property
    def get_payload(self):
        return self.payload

    @property
    def get_config_diff(self):
        flattened_payload = self.__flatten_dict(self.payload_items)
        flattened_target_config = self.__flatten_dict(self.target_config)
        diff_item_keys = self.__list_diff_item_keys(flattened_payload, flattened_target_config)
        diff_dict = {}
        for key in diff_item_keys:
            diff_dict.update(
                {key: {"payload_value": flattened_payload[key], "target_value": flattened_target_config[key]}})
        return diff_dict

    # Pour debug
    @property
    def get_diff_keys(self):
        return  self.__list_diff_item_keys(self.payload, self.target_config)

    # Pour debug
    @property
    def get_diff_item_keys(self):
        return self.diff_item_keys

    def __format_payload_items(self, payload_items, payload_template):
        validators = self.__flatten_dict(payload_template)
        formatted_payload_items = {}
        for key in payload_items.keys():
            item_value = payload_items[key]
            # TODO check if it's compatible with other workflow to add not == ""
            if (item_value is not None) and (item_value != ""):
                if key in validators:
                    # TODO check if the line below is needed considering that item_value already contains "payload_items[key]"
                    item_value = payload_items[key] 
                    item_value = self.__format_payload_item(key, item_value, validators[key])
                    formatted_payload_items.update({key: item_value})
        return formatted_payload_items


    """[This method first validate a value and then format it]
    
    Raises:
        InvalidPayloadItem: [description]
    
    Returns:
        [object] -- [Return the formatted value or None]
    """
    def __format_payload_item(self, key, value, validation_data):
        value_type = validation_data[0]
        validation_value = validation_data[1:]
        error_msg = f"The playload item \'{key}: {value}\' is invalid. The value test is: {validation_value}"
        return_value = None
        if (value_type == "regex"):
            match = fullmatch(validation_value[0], value)
            if match:
                return_value = value
            else:
                raise InvalidPayloadItem(error_msg)
        elif (value_type == "range"):
            if (validation_value[0] <= int(value) <= validation_value[1]):
                return_value =  str(value)
            else:
                raise InvalidPayloadItem(error_msg)
        elif (value_type == "bool"):
            if (bool(value) == 1 or bool(value) == 0):
                return_value =  str(int(value))
        elif (value_type == "choices"):
            if value in validation_value:
                return str(value)
            else:
                raise InvalidPayloadItem(error_msg)
        elif (value_type == "str"):
            return str(value)
        elif (value_type == "ip"):
            match = fullmatch(IP_ADDRESS_REGEX, self.clean_ip(value))
            if match:
                return_value = value
            else:
                raise InvalidPayloadItem(error_msg)
        return return_value

    def build_payload(self, payload_template):
        self.diff_item_keys = self.__list_diff_item_keys(self.payload_items, self.__flatten_dict(self.target_config))
        return self.__build_payload_dict(payload_template)


    """[This method recursively create a dictionnary based on the payload_node
    dictionnary structure and insert the values found in self.payload_items]
    
    Returns:
        [dict] -- [Returns a dictinnary containing the payload values]
    """
    def __build_payload_dict(self, payload_node):
        payload = {}
        for key in payload_node.keys():
            payload_node_value = payload_node[key]
            if isinstance(payload_node_value, dict):
                leaf_value = self.__build_payload_dict(payload_node_value)
                if leaf_value:
                    payload.update({key: leaf_value})
            elif key in self.diff_item_keys:
                payload.update({key: self.payload_items[key]})
        return payload


    """[This method take a dict and flattens it]
    
    Returns:
        [dict] -- [Returns the flattened dict]
    """
    def __flatten_dict(self, base_dict):
        flattened_dict = {}
        for key in base_dict.keys():
            if isinstance(base_dict[key], dict):
                flattened_dict.update(self.__flatten_dict(base_dict[key]))
            else:
                flattened_dict.update({key:base_dict[key]})
        return flattened_dict


    """[Create a list containing the keys for all the items having different value
    between the two input dictionnaries]
    
    Returns:
        [list] -- [List containing the keys]
    """
    def __list_diff_item_keys(self, primary_dict, target_dict):
        diff_item_keys = []
        for key in primary_dict.keys():
            if primary_dict[key]:
                if key in target_dict:
                    if not primary_dict[key] == target_dict[key]:
                        diff_item_keys.append(key)
        return diff_item_keys


    """[Get target configuration]
    
    Raises:
        ConnexionError: [description]
    
    Returns:
        [dict] -- [Response from target]
    """
    def get_target_config(self):
        try:
            response = get(self.url)
            response.raise_for_status()
        except Exception:
            raise
        else:
            try:
                return response.json()
            except json.decoder.JSONDecodeError:
                return {'msg': "value can't be parsed to json."}

    """[Send configuration payload to module]
    
    Raises:
        KeyError: [description]
        ConnexionError: [description]
        ModuleNotConfiguredError: [description]
    
    Returns:
        [str] -- [Result message]
    """
    def send_configuration(self, validate_changes=True):
        inital_comp = self.get_config_diff
        # Dans certains cas, le module reset avant d'envoyer une réponse. L'opération fonctionne mais on a une erreur
        try:
            put_response = put(self.url, data=json.dumps(self.payload))
        except:
            pass
        self.target_config = self.get_target_config()
        if validate_changes:
            result_comp = self.get_config_diff
            flattened_target_config = self.__flatten_dict(self.target_config)
            trimmed_response = {key:flattened_target_config[key] for key in flattened_target_config.keys() if key in self.diff_item_keys}
            if not result_comp:
                msg = f"Configuration successful!\nPayload:\n{dump(self.payload, default_flow_style=False)}\nProgrammed values:\n{dump(trimmed_response, default_flow_style=False)}"
                return msg
            else:
                error_msg = f"Some changes weren\'t made: {dump(result_comp, default_flow_style=False)}"
                raise ModuleNotConfiguredError(error_msg)
        else:
            msg = f"Payload sent!\nPayload:\n{dump(self.payload, default_flow_style=False)}"
            return msg

    """[Send downloaded configuration from module to the same module. Should only be use with the previously downloaded configuration.]

    Returns:
        [dict] -- [Result message]
    """
    def send_downloaded_configuration(self):
        key_only_in_payload_to_send_list = []
        key_only_in_target_module_list = []
        self.target_config = self.get_target_config()
      
        for key in self.payload.keys():
            if key not in self.target_config.keys():
                key_only_in_payload_to_send_list(key)
            else:
                if type(self.payload[key]) == dict:
                    for subkey in self.payload[key]:
                        if subkey not in self.target_config[key].keys():
                            key_only_in_payload_to_send_list.append(key+"{"+subkey+"}")

        for key in self.target_config.keys():
            if key not in self.payload.keys():
                key_only_in_target_module_list.append(key)
            else:
                if type(self.target_config[key]) == dict:
                    for subkey in self.target_config[key]:
                        if subkey not in self.payload[key].keys():
                            key_only_in_target_module_list.append(key+"{"+subkey+"}")

        try:
            put_response = put(self.url, data=json.dumps(self.payload))
        except:
            pass
        return {
            'msg': 'Payload sent!',
            'key_only_in_target_module_list': key_only_in_target_module_list,
            'key_only_in_payload_to_send_list': key_only_in_payload_to_send_list
        }