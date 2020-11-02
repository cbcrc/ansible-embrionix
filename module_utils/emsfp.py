#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from requests import get, put
from requests import exceptions as ReqException
from collections.abc import Iterable
from re import fullmatch
from yaml import dump as yaml_dump
from time import sleep
from json import dumps as json_dumps
from json.decoder import JSONDecodeError
from ipaddress import IPv4Address,IPv4Network
# from collections import OrderedDict
from pprint import pprint
from logging import getLogger

emsfp_log = getLogger(__name__)

# Verifie que les valeurs entrées sont de 0.0.0.0 à 255.255.255.255.
IP_ADDRESS_REGEX = "^(([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))$"

SDI_CHANNEL_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}:([0-9]|1[0-5]):[0,1]$"
SDI_CHANNEL_ID_REGEX = "^b[0-7][0-9a-f]{6}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
NAME_REGEX = "^[-\s\w\W]{1,25}$"
LABEL_REGEX = "^[-\s\w\W]{1,16}$"
REF_CLOCK_ID = "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
HOSTNAME_REGEX = "^[-\s\w\W]*$"

class EmbrionixError(Exception):
    pass

class InvalidPayloadItem(EmbrionixError):
    def __init__(self, key, value, reference):
        self.__message = f"The playload item \'{key}: {value}\' is invalid. The reference values are: {reference}"

class BuildPayloadError(EmbrionixError):
    def __init__(self, message):
        self.__message = message

class ConnexionError(EmbrionixError):
    pass

class ModuleNotConfiguredError(EmbrionixError):
    def __init__(self, message, items_not_configured={}):
        self.__message = message
        self.__items_not_configured = items_not_configured

# class InvalidFilteringOption(EmbrionixError):
#     def __init__(self, )

class EMSFP(object):
    """
    EMSFP [summary]

    Args:
        object ([type]): [description]
    """
    def __init__(self, url: str = "", payload_params: dict = {}, in_payload_template: dict = {}):
        """
        __init__ initialize the EMSFP instance

        Args:
            url (str, optional): The Embrionix device ip address. Defaults to "".
            payload_params (dict, optional): The payload to send parameters. Defaults to {}.
            in_payload_template (dict, optional): Payload template for validation purpose. Defaults to {}.
        """
        self.__url = url
        self.__payload = {}
        self.__payload_params = payload_params
        self.__payload_template = in_payload_template
        self.__payload_values_dict = payload_params
        self.__target_config_dict = {}

        emsfp_log.info(f"self.__payload_params: {self.__payload_params}")
        if self.__url != "":
            emsfp_log.info(f"URL: {self.__url}")
            self.__target_config_dict = self.__get_target_config()
            if payload_params != {}:
                self.build_payload()

    @property
    def get_config_diff(self) -> dict:
        diff = self.__diff_dict(self.__payload, self.__target_config_dict)
        emsfp_log.info(f"config diff: {diff}")
        return diff

    @property
    def payload(self) -> dict:
        return self.__payload

    @property
    def payload_template(self) -> dict:
        return self.__payload_template_dict

    @payload_template.setter
    def payload_template(self, payload_template: dict):
        self.__payload_template = payload_template

    @property
    def payload_params(self) -> dict:
        return self.__payload_params

    @payload_params.setter
    def payload_params(self, payload_params: dict):
        self.__payload_params = payload_params

    @property
    def payload_values(self) -> dict:
        return self.__payload_values_dict

    @property
    def target_config(self) -> dict:
        return self.__target_config_dict

    @property
    def url(self) -> str:
        return self.__url

    @url.setter
    def url(self, url: str):
        self.__url = url

    def build_payload(self):
        """
        build_payload build the configuration payload only with configuration values differing between initially provided payload and actual target configured values.

        Raises:
            BuildPayloadError: error captured during payload creation
        """
        try:
            self.__payload = self.__diff_dict(self.__payload_values_dict, self.__target_config_dict)
            emsfp_log.info(f"Built payload: {self.__payload}")
        except Exception as e:
            msg = f"Route: {self.__url}\nPayload_values:\n{self.payload_values}\nTarget config:\n{self.target_config}\n{e}"
            raise BuildPayloadError(msg)

    def download_target_config(self):
        """download_target_config download, flatten and store target configuration in self.__target_config."""
        self.__target_config_dict = self.__get_target_config()

    def get_api_data(self, url: str) -> str:
        """
        get_api_data return api response for route.

        Args:
            url (str): api endpoint route

        Returns:
            str: device response
        """
        try:
            res = get(url)
            return res.json()
        except Exception as e:
            msg = f"Route: {url} failed with error {e}"
            return msg

    def get_all_routes(self, base_route: str = "", key_filter: tuple = (), ignored_route_filter: tuple = ()) -> dict:
        """
        get_all_routes return a dict containing the key:value for all route in key_filter and not in ignored_route_filter. Values can be nested dict.

        Args:
            base_route (str, optional): the route to return key:value from. Defaults to "".
            key_filter (tuple, optional): tuple of string representing the considered keys. Defaults to ().
            ignored_route_filter (tuple, optional): tuple of string for all routes that should be avoided. Defaults to ().

        Returns:
            [dict]: containing all the key:value returned from the device api
        """
        route_dict = {}
        if base_route == "":
            base_route = self.__url
        routes = self.__get_target_config(base_route)
        for route in routes:
            if str(route).endswith('/') and route not in ignored_route_filter:
                route_str = f"{base_route}{route}"
                route_value = self.get_all_routes(f"{route_str}", key_filter=key_filter, ignored_route_filter=ignored_route_filter)
                if route_value:
                    k = route.rstrip("/")
                    route_dict.update({k:route_value})
            # TODO this could probably be removed. It breaks when value is a list of dict, like some 'network':value
            # elif isinstance(routes, dict) and isinstance(routes[route], list):
            #     temp_dict = {}
            #     for element in routes[route]:
            #         try:
            #             if element not in ignored_route_filter:
            #                 route_str = f"{base_route}{element}/"
            #                 # if isinstance(route_value, list):
            #                 route_value = self.get_all_routes(f"{route_str}", key_filter=key_filter, ignored_route_filter=ignored_route_filter)
            #                 if route_value:
            #                     temp_dict.update({element:route_value})
            #         except Exception:
            #             pass #no need to do anything if it doesn't work
            #     if temp_dict:
            #             route_dict.update({route:temp_dict})
            elif isinstance(routes, dict) and isinstance(routes[route], dict):
                if route in key_filter and routes[route] != {}: 
                    old_dict = routes[route]
                    filtered_dict = {k: old_dict[k] for k in old_dict if k in key_filter}
                    route_dict.update({route:filtered_dict})
            elif route in key_filter and routes[route]:
                route_dict.update({route:routes[route]})
        return route_dict


    def send_configuration(self, validate_changes: bool = True, wait_for_device_reboot: int = 20) -> str:
        """
        send_configuration send configuration payload the the device, the check if configuration is successful.

        Args:
            validate_changes (bool, optional): validate configuration changes or not. Defaults to True.
            wait_for_device_reboot (int, optional): time in seconds to wait for after reboot. Defaults to 0.

        Raises:
            ModuleNotConfiguredError: when configuration failed

        Returns:
            [str]: the configuration result message
        """
        inital_comp = self.get_config_diff
        if inital_comp == {}:
            return f"Payload is empty, nothing to send."
        emsfp_log.info(f"Sent payload (self.__payload): {self.__payload}")
        # In some cases, the module reset without sending an answer. The module is successfuly configured, but an error is generated
        put_response = None
        try:
            response = put(self.url, data=json_dumps(self.__payload))

            if response.status_code != 200:
                emsfp_log.error(f"Put response code: {response.status_code}")
                emsfp_log.error(f"Put response reason: {response.reason}")
            else:
                emsfp_log.info(f"Put response code: {response.status_code}")
                put_response = response.json()
                if 'info' in put_response:
                    if  put_response['info'] == "system rebooting" and "self/system/" in self.__url:
                        msg = f"Device reboot in progress!"
                        if not validate_changes:
                            return msg
                        else:
                            self.__wait_for_connection(retries=wait_for_device_reboot)
        except JSONDecodeError as e:
            emsfp_log.info(f"json decoding error: {e}")
            raise e
        except Exception as e:
            emsfp_log.info(f"put exception: {e}")
            pass
        if put_response == None:
            emsfp_log.info(f"No response from module")
        else:
            emsfp_log.info(f"Response: {put_response}")
        # sleep(wait_for_device_reboot)
        target_config = self.__get_target_config()

        if validate_changes:
            payload_diff_target = {}
            # In case device reset before sending a response
            if put_response == None:
                payload_diff_target = self.__diff_dict(self.__payload, self.__target_config_dict)
            elif put_response == self.__payload:
                    emsfp_log.info(f"put_response == self._payload: {put_response}")
                    payload_diff_target = {}
            if payload_diff_target == {}:
                msg = f"Configuration successful!\nPayload:\n{yaml_dump(self.payload, default_flow_style=False)}\nProgrammed values:\n{yaml_dump(put_response, default_flow_style=False)}"
                return msg
            else:
                error_msg = f"Some changes weren\'t made:\n{yaml_dump(payload_diff_target, default_flow_style=False)}\nPut response: {json_dumps(put_response)}"
                raise ModuleNotConfiguredError(error_msg)
        else:
            msg = f"Payload sent with no validation:\nPayload:\n{yaml_dump(self.__payload, default_flow_style=False)}"
            return msg

    def __diff_dict(self, dict1: dict, dict2: dict) -> dict:
        """
        __diff_dict Compare dict1 and dict2 and return a dict containing only the key:value from \
                    the reference dictionnary dict1 that differs from the comparison dictionnary dict2. \
                    Values that are empty strings are filtered out.

        Args:
            dict1 (dict): The reference dictionnary
            dict2 (dict): The comparison dictionnary

        Raises:
            KeyError: when a key in dict1 isn't present in dict2

        Returns:
            dict: containing element in dict1 that differs from dict2 and whose value aren't empty string
        """
        result_dict = {}
        for key in dict1:
            if key in dict2:
                temp_value = None
                emsfp_log.info(f"Values for key({key}): dict1 -> {dict1[key]}({type(dict1[key])}), dict2 -> {dict2[key]}({type(dict1[key])})")
                if isinstance(dict1[key], dict):
                    emsfp_log.info(f"Case dict; Value for key({key}) is instance of: {type(dict1[key])}; call to self.__diff_dict")
                    temp_value = self.__diff_dict(dict1[key], dict2[key])
                elif isinstance(dict1[key], list):
                    emsfp_log.info(f"Case list; Value for key({key}) is instance of: {type(dict1[key])}; call to self.__diff_list")
                    try:
                        temp_value = self.__diff_list(dict1[key], dict2[key])
                    except Exception as e:
                        raise(e)
                elif isinstance(dict1[key], str) and isinstance(dict2[key], str) and (dict1[key] != "") and (dict1[key].capitalize() != dict2[key].capitalize()):
                #value comparison is capitalised so that, for exemple, 'ff00' equals 'FF00'.
                    emsfp_log.info(f"Case 3; dict1[{key}]:'{dict1[key]}'({type(dict1[key])}); dict2[{key}]:'{dict2[key]}'({type(dict2[key])})")
                    temp_value = dict1[key]

                if temp_value and temp_value != '':
                    emsfp_log.info(f"Add key({key}):value '{temp_value}'({type(temp_value)}); dict2 value '{dict2[key]}'({type(dict2[key])})")
                    result_dict[key] = temp_value
        emsfp_log.info(f"Resulting dict: {result_dict}")
        return result_dict

    def __diff_list(self, list1: list, list2: list) -> list:
        """
        __diff_list Compare list1 and list2 and return a list containing items from list1 that are different \
                    from the item at the same index in list2.

        Args:
            list1 (list): The reference list
            list2 (list): The comparison list

        Returns:
            list: containing elements with matching index from list1 and list2 that are different.
        """
        result_list = []
        for i, item in enumerate(list1):
            temp_elem = None
            try:
                emsfp_log.info(f"Value for item({i}) is instance of: {type(list1[i])}, value: {list1[i]}")
                if list1[i] != list2[i]:
                    if isinstance(list1[i], list):
                        emsfp_log.info(f"Case list; Value for item({i}) is instance of: {type(list1[i])}); call to self.__diff_list")
                        temp_elem = self.__diff_iterable(list1[i], list2[i])
                    elif isinstance(list1[i], dict):
                        emsfp_log.info(f"Case dict; Value for item({i}) is instance of: {type(list1[i])}); call to self.__diff_dict")
                        temp_elem = self.__diff_dict(list1[i], list2[i])
                    elif (list1[i] != "") and (str(list1[i]) != str(list2[i])):
                        emsfp_log.info(f"Case 3; Value for item({i}) is instance of: {type(list1[i])});")
                        temp_elem = list[i]
            except IndexError:
                if list1[i] != "":
                    temp_elem = list[i]
                temp_elem = list1[i]
            except Exception as e:
                raise(e)
            if temp_elem:
                emsfp_log.info(f"Append item({i}):value({list1[i]}, instance of {type(list1[i])})")
                result_list.append(temp_elem)
        emsfp_log.info(f"Resulting list: {result_list}")
        return result_list

    def __format_payload_items(self, payload_items: dict, payload_template: dict) -> dict:
        """
        __format_payload_items [summary].

        Args:
            payload_items ([type]): [description]
            payload_template ([type]): [description]

        Returns:
            [type]: [description]
        """
        validators = payload_template
        formatted_payload_items = {}
        if payload_template == {}:
            formatted_payload_items = payload_items
        else:
            for key in payload_items:
                item_value = payload_items[key]
                # TODO check if it's compatible with other workflow to add not == ""
                if (item_value is not None) and (item_value != ""):
                    if key in validators:
                        # TODO check if the line below is needed considering that item_value already contains "payload_items[key]"
                        item_value = payload_items[key]
                        item_value = self.__validate_item(key, item_value, validators[key])
                        formatted_payload_items.update({key: item_value})
        return formatted_payload_items


    def __get_target_config(self, url: str = "") -> dict:
        """
        __get_target_config [summary].

        Args:
            url (str, optional): [description]. Defaults to "".

        Raises:
            EmbrionixError: [description]

        Returns:
            [type]: [description]
        """
        if url == "":
            url = self.__url
        try:
            response = get(url)
            response.raise_for_status()
        except Exception as e:
            raise EmbrionixError(f"Module unreachable: {e}")
        else:
            try:
                emsfp_log.info(f"Downloaded target config {response.json()}")
                return response.json()
            except JSONDecodeError:
                return {'msg': "value can't be parsed to json."}


    def __validate_item(self, key, value, validation_data):
        """
        __validate_item [summary].

        Args:
            key ([type]): [description]
            value ([type]): [description]
            validation_data ([type]): [description]

        Returns:
            [type]: [description]
        """
        value_type = validation_data[0]
        reference = validation_data[1:]
        return_value = None
        if value_type == "regex":
            return_value = self.__validate_regex(key, value, reference)
        elif value_type == "hostname":
            return_value = self.__validate_regex(key, value, [HOSTNAME_REGEX])
        elif value_type == "range":
            return_value = self.__validate_range(key, value, reference)
        elif value_type == "bool":
            if (bool(value) == 1 or bool(value) == 0):
                return_value = str(int(value))
        elif value_type == "choices":
            return_value = self.__validate_choices(key, value, reference)
        elif value_type == "str":
            return_value = str(value)
        elif value_type == "ip":
            return_value = self.__validate_ip(key, value, reference)
            # pass
        return return_value

    def __validate_choices(self, key, value, reference):
        if value in reference:
            return str(value)
        raise InvalidPayloadItem(key, value, reference)

    def __validate_range(self, key, value, reference):
        if int(reference[0]) <= int(value) <= int(reference[1]):
            return str(value)
        raise InvalidPayloadItem(key, value, reference)

    def __validate_regex(self, key, value, reference):
        match = fullmatch(reference[0], value)
        if match:
            return value
        raise InvalidPayloadItem(key, value, reference)

    def __validate_ip(self, key, value, reference):
        formatted_value = str(IPv4Address(value))
        match = fullmatch(IP_ADDRESS_REGEX, value)
        if match:
            return formatted_value
        raise InvalidPayloadItem(key, formatted_value, reference)

    def __wait_for_connection(self, retries: int = 200, delay: int = 0.1) -> None:
        """
        __wait_for_connection [summary].

        Args:
            retries (int, optional): [description]. Defaults to 20.
            delay (int, optional): [description]. Defaults to 0.1.

        Raises:
            ReqException.HTTPError: [description]
        """
        while(retries > 0):
            try:
                sleep(delay)
                response = get(self.url)
                response.raise_for_status()
                if response.status_code == 200:
                    response_json = response.json()
                    if 'info' in response_json:
                        if response_json['info'] != "system rebooting":
                            return
                    else:
                        return
                else:
                    raise ReqException.HTTPError(response.status_code)
            except (
                Exception,
                ReqException.ConnectionError,
                ReqException.Timeout,
                ReqException.RequestException,
                ReqException.BaseHTTPError,
                ReqException.ConnectTimeout,
                ReqException.RetryError) as e:
                pass
            finally:
                retries -= retries
