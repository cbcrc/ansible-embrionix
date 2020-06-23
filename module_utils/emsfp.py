#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from requests import get, put
from requests import exceptions as ReqException
from re import fullmatch
from yaml import dump as yaml_dump
from module_utils.flatdict import FlatDict
from time import sleep
from json import dumps as json_dumps
from json.decoder import JSONDecodeError
from ipaddress import IPv4Address,IPv4Network
from collections import OrderedDict
from pprint import pprint
import logging


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
    def __init__(self, url="", payload_params={}, in_payload_template={}):
        """
        __init__ [summary]

        Args:
            url (str, optional): [description]. Defaults to "".
            payload_params (dict, optional): [description]. Defaults to {}.
            in_payload_template (dict, optional): [description]. Defaults to {}.
        """
        FORMAT = '%(asctime)-15s - %(name)s, %(lineno)d - %(levelname)s - %(message)s'
        logging.basicConfig(filename='logs/emsfp.log', filemode='a', format=FORMAT, level=logging.INFO)
        self.emsfp_log = logging.getLogger("emsfp")

        self.__url = url
        self.__payload = {}
        self.__payload_params = payload_params
        self.__payload_template = FlatDict(in_payload_template)
        # self.emsfp_log.info(f"__payload_template: {self.__payload_template}")
        self.__payload_values = FlatDict(self.__format_payload_items(FlatDict(payload_params), self.__payload_template))
        # self.emsfp_log.info(f"__payload_values: {self.__payload_values}")
        self.__target_config = FlatDict({})
        # self.emsfp_log.info(f"__target_config: {self.__target_config}")
        if self.url != "":
            self.__target_config = FlatDict(self.__get_target_config())
            if payload_params != {} and in_payload_template != {}:
                self.build_payload()
                # self.emsfp_log.info(f"__payload: {self.__payload}")

    @property
    def get_config_diff(self):
        return FlatDict(self.__build_config_diff_dict())

    @property
    def payload(self):
        return self.__payload

    @property
    def payload_template(self):
        # emsfp_log.info("----------------------------------------------------------")
        return self.__payload_template.get_unflattened_dict()

    @payload_template.setter
    def payload_template(self, payload_template):
        self.__payload_template = FlatDict(payload_template)

    @property
    def payload_params(self):
        return self.__payload_params

    @payload_params.setter
    def payload_params(self, payload_params):
        self.__payload_params = FlatDict(payload_params)

    @property
    def payload_values(self):
        # emsfp_log.info("----------------------------------------------------------")
        return self.__payload_values.get_unflattened_dict()

    @property
    def target_config(self):
        # emsfp_log.info("----------------------------------------------------------")
        return self.__target_config.get_unflattened_dict()

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url

    def build_payload(self):
        """
        build_payload [summary]

        Raises:
            BuildPayloadError: [description]
        """
        try:
            diff_items = FlatDict(self.__build_config_diff_dict())
            self.emsfp_log.info(f"build_payload ->  diff_items: {diff_items}")
            # self.emsfp_log.info("----------------------------------------------------------")
            self.__payload = diff_items.get_unflattened_dict()
            self.emsfp_log.info(f"build_payload -> builded payload: {self.__payload}")
        except Exception as e:
            msg = f"Route: {self.__url}\nPayload_values:\n{self.payload_values}\nTarget config:\n{self.target_config}\n{e}"
            self.emsfp_log.info(f"Erreur build payload: {e}")
            raise BuildPayloadError(msg)

    def download_target_config(self):
        """
        download_target_config [summary]
        """
        self.__target_config = FlatDict(self.__get_target_config())
        # self.emsfp_log.info(f"download_target_config -> self.__target_config: {self.__target_config}")


    def get_all_routes(self, base_route="", key_filter=(), ignored_route_filter=()):
        """
        get_all_routes [summary]

        Args:
            base_route (str, optional): [description]. Defaults to "".
            key_filter (tuple, optional): [description]. Defaults to ().
            ignored_route_filter (tuple, optional): [description]. Defaults to ().

        Returns:
            [type]: [description]
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
            elif isinstance(routes, dict) and isinstance(routes[route], list):
                temp_dict = {}
                for element in routes[route]:
                    try:
                        if element not in ignored_route_filter:
                            route_str = f"{base_route}{element}/"
                            route_value = self.get_all_routes(f"{route_str}", key_filter=key_filter, ignored_route_filter=ignored_route_filter)
                            if route_value:
                                temp_dict.update({element:route_value})
                    except Exception:
                        pass #no need to do anything if it doesn't work
                if temp_dict:
                        route_dict.update({route:temp_dict})
            elif isinstance(routes, dict) and isinstance(routes[route], dict):
                if route in key_filter and routes[route] != {}: 
                    old_dict = routes[route]
                    filtered_dict = {k: old_dict[k] for k in old_dict if k in key_filter}
                    route_dict.update({route:filtered_dict})
            elif route in key_filter and routes[route]:
                route_dict.update({route:routes[route]})
        return route_dict

    def get_all_routes_flattened(self):
        """
        get_all_routes_flattened [summary]

        Returns:
            [type]: [description]
        """
        return FlatDict(self.get_all_routes())

    def send_configuration(self, validate_changes=True, wait_for_device_reboot=0):
        """
        send_configuration [summary]

        Args:
            validate_changes (bool, optional): [description]. Defaults to True.
            wait_for_device_reboot (int, optional): [description]. Defaults to 0.

        Raises:
            ModuleNotConfiguredError: [description]

        Returns:
            [type]: [description]
        """
        inital_comp = FlatDict(self.get_config_diff)
        mess = ""
        self.emsfp_log.info(f"Sent payload (self.__payload): {self.__payload}")
        # In some cases, the module reset without sending an answer. The module is successfuly configured, but an error is generated
        try:
            put_response = put(self.url, data=json_dumps(self.__payload)).json()
            # if 'info' in put_response:
            #     if  put_response['info'] == "system rebooting":
            #         self.__wait_for_connection(retries=wait_for_device_reboot)
        #TODO escape only the cases where the module doesn't answer
        except Exception:
            pass
        sleep(wait_for_device_reboot)
        target_config = FlatDict(self.__get_target_config())
        if validate_changes:
            result_comp = self.get_config_diff
            flat_payload = FlatDict(self.__payload)
            payload_in_target = target_config.include_dict(flat_payload)
            trimmed_response = FlatDict({key:target_config[key] for key in target_config if key in flat_payload})
            if payload_in_target:
                # emsfp_log.info("----------------------------------------------------------")
                msg = f"Configuration successful!\nPayload:\n{yaml_dump(self.payload, default_flow_style=False)}\nProgrammed values:\n{yaml_dump(trimmed_response.get_unflattened_dict(), default_flow_style=False)}"
                return msg
            else:
                # emsfp_log.info("----------------------------------------------------------")
                error_msg = f"Some changes weren\'t made:\n{yaml_dump(result_comp, default_flow_style=False)}\nPut response: {json_dumps(target_config.get_unflattened_dict())}"
                raise ModuleNotConfiguredError(error_msg)
        else:
            msg = f"Payload sent with no validation:\nPayload:\n{yaml_dump(self.__payload, default_flow_style=False)}"
            return msg

    #TODO le nombre variable d'éléments dans le mapping audio cause des erreurs dans return self.__payload_values.diff(flattened_target_config)

    def __build_config_diff_dict(self):
        """
        __build_config_diff_dict [summary]

        Returns:
            [type]: [description]
        """
        flattened_target_config = FlatDict(self.__get_target_config())
        self.emsfp_log.info(f"__build_config_diff_dict -> flattened_target_config: {flattened_target_config}")
        # Make sure all values are strings for comparison
        for key in flattened_target_config.keys():
            flattened_target_config[key] = str(flattened_target_config[key])
        self.emsfp_log.info(f"__build_config_diff_dict -> flattened_target_config: {flattened_target_config}")
        self.emsfp_log.info(f"__build_config_diff_dict -> self.__payload_values  : {self.__payload_values}")
        return self.__payload_values.diff(flattened_target_config, add_missing_key=True)


    def __build_payload_dict(self, payload_node):
        """
        __build_payload_dict [summary]

        Args:
            payload_node ([type]): [description]

        Returns:
            [type]: [description]
        """
        payload = {}
        for key in payload_node.keys():
            payload_node_value = payload_node[key]
            if isinstance(payload_node_value, dict):
                leaf_value = self.__build_payload_dict(payload_node_value)
                if leaf_value:
                    payload.update({key: leaf_value})
            # elif key in self.diff_item_keys:
                else:
                    payload.update({key: self.__payload_values[key]})
        return payload

    def __format_payload_items(self, payload_items, payload_template):
        """
        __format_payload_items [summary]

        Args:
            payload_items ([type]): [description]
            payload_template ([type]): [description]

        Returns:
            [type]: [description]
        """
        validators = payload_template
        formatted_payload_items = {}
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


    def __get_target_config(self, url=""):
        """
        __get_target_config [summary]

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
                return response.json()
            except JSONDecodeError:
                return {'msg': "value can't be parsed to json."}


    def __validate_item(self, key, value, validation_data):
        """
        __validate_item [summary]

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

    def __wait_for_connection(self, retries=5, delay=2):
        """
        __wait_for_connection [summary]

        Args:
            retries (int, optional): [description]. Defaults to 5.
            delay (int, optional): [description]. Defaults to 2.

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
