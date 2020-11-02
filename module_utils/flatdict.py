#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from collections.abc import MutableMapping
import logging
from pprint import pprint

# FORMAT = '%(asctime)-15s - %(name)s, %(lineno)d - %(levelname)s - %(message)s'
# logging.basicConfig(filename='flat_dict.log', filemode='a', format=FORMAT, level=logging.INFO)
# flat_dict_log = logging.getLogger("flat_dict")

class FlatDictException(Exception):
    pass

class FlatDictKeyError(FlatDictException):
    pass

class FlatDict(MutableMapping):
    """
    FlatDict Take a multi-level dictionnary and flatten it to one level.

    Args:
        MutableMapping ([type]): [description]
    """
    def __init__(self, *args, **kwargs):
        self.flat_dict = dict()
        if args:
            if isinstance(args[0], dict):
                if args[0] != {}:
                    self.update(self.__flatten_dict(dict(*args, **kwargs)))
            elif isinstance(args[0], FlatDict):
                if args[0] != {}:
                    self.update(dict(*args, **kwargs))

    def __cmp__(self, flat_dict_):
        return self.flat_dict.__cmp__(self.flat_dict, flat_dict_)

    def __contains__(self, item):
        return item in self.flat_dict

    def __getitem__(self, key):
        return self.flat_dict[key]

    def __setitem__(self, key, value):
        self.flat_dict[key] = value

    def __delitem__(self, key):
        del self.flat_dict[key]

    def __iter__(self):
        return iter(self.flat_dict)

    def __len__(self):
        return len(self.flat_dict)

    def __str__(self):
        return self.__print_flat_dict(self.flat_dict)

    def __repr__(self):
        return self.__print_flat_dict(self.flat_dict, new_line=True)

    def clear(self):
        return self.flat_dict.clear()

    def copy(self):
        return self.flat_dict.copy()

    def pop(self):
        return self.flat_dict.pop()

    def popitem(self):
        return self.flat_dict.popitem()

    def keys(self):
        return self.flat_dict.keys()     

    def unflatten(self):
        """
        unflatten returns an unflattened version of the flattened dictionary. The resulting dictionary should
        be identical to the original dictionary.

        Returns:
            (dict): an unflattened version of the flattened dictionary
        """
        return self.__build_unflattened_dict(self.flat_dict)

    def __flatten_dict(self, base_dict, last_key = ''):
        """
        __flatten_dict takes a multi-level dictionary and returns a dictionary flattened to one level.

        Args:
            base_dict (dict): the dictionary to flatten
            last_key (str, optional): the key from the last dictonary level. Used to build the complete key with recursion. Defaults to ''.

        Returns:
            (dict): the flattened dictionary
        """
        flattened_dict = {}
        if base_dict.keys() is not None:
            for key in base_dict.keys():
                if isinstance(base_dict[key], dict):
                    if last_key == '':
                        flattened_dict.update(self.__flatten_dict(base_dict[key], key))
                    else:
                        flattened_dict.update(self.__flatten_dict(base_dict[key], last_key + '|-|' + key))
                elif last_key == '':
                    flattened_dict.update({key:base_dict[key]})
                else:
                    flattened_dict.update({last_key + '|-|' + key:base_dict[key]})
            return flattened_dict
        else:
            return dict()

    def __print_flat_dict(self, fd, new_line=False):
        """
        __print_flat_dict creates the output for the print function.

        Args:
            fd (dict): flat dictionary instance
            new_line (bool, optional): add new line if true, doesn't otherwise. Defaults to False.

        Returns:
            [type]: [description]
        """
        string = "{"
        if new_line:
            string = string + "\n"
        for key in fd:
            string = string + f"\'{key}\': {fd[key]}, "
            if new_line:
                string = string + "\n"
        if string.endswith(', '):
            string = string[:-2]
        return string + "}"


    def __build_unflattened_dict(self, flattened_dict):
        """
        __build_unflattened_dict Takes a one-level flattened dictionary and build an unflattened version.

        Args:
            flattened_dict (FlatDict): A flattened dictionnary

        Returns:
            (dict): The unflattened dictionnary.
        """
        base_dict = {}
        for key in flattened_dict.keys():
            elements = key.split('|-|')
            item = {elements.pop(): flattened_dict[key]}
            base_dict = self.__insert_in_dict(base_dict, elements, item)
        return base_dict

    def __insert_in_dict(self, target_dict, key_list, item):
        """
        __insert_in_dict Insert the key: value item into the multi-level target_dict, each level corresponding the the keys in key_list, and \
                         return the resulting dictionnary.

        Args:
            target_dict (dict): the dictionnary into wich the item will be inserted
            key_list (list<string>): a list of dictionnay keys, each corresponding to a subdictionnary key, starting with the first (index 0)
                                     for target_dict
            item (dict): a sigle {key: value} pair

        Returns:
            (dict): a dictionnary containing the inserted item
        """
        if not key_list:
            target_dict.update(item)
        else:
            key = key_list.pop(0)
            if key in target_dict:
                target_dict[key].update(self.__insert_in_dict(target_dict[key], key_list, item))
            else:
                target_dict.update({key: {}})
                target_dict[key].update(self.__insert_in_dict(target_dict[key], key_list, item))
        return target_dict

    #TODO enlever le fix dans le check pour une clef non présente
    def diff(self, reference_dict: dict, add_missing_key: bool = False) -> dict:
        """
        diff returns a dict containing the elements whose the value differs from the reference dictionary.

        Args:
            reference_dict (dict): the dictionary to compare with.

        Raises:
            ValueError: when the provided reference_dict isn't an instance of FlatDict ou dict.
            FlatDictKeyError: when a key prensent in self doen't exists in the reference_dict.

        Returns:
            (dict): a dictionary contaning the items with different values
        """
        diff_dict = {}
        if isinstance(reference_dict, dict):
            flattened_reference_dict = self.__flatten_dict(reference_dict)
        elif isinstance(reference_dict, FlatDict):
            flattened_reference_dict = reference_dict
        else:
            raise ValueError('Provided object is not an instance of dict or FlatDict')
        # temp_dict = self.flat_dict.copy()
        for key in self.flat_dict:
            if key not in flattened_reference_dict:
                if add_missing_key:
                    diff_dict.update({key: self.flat_dict[key]})
                else:
                    raise FlatDictKeyError(f"Key '{key}' not present in provided object: {flattened_reference_dict}")
            elif self.flat_dict[key] != flattened_reference_dict[key]:
                diff_dict.update({key: self.flat_dict[key]})
        return diff_dict


    def key_diff(self, reference_dict):
        """ [summary]
        
        Returns:
            differences in keys from self.flat_dict to reference_dict
            differences in keys from reference_dict to self.flat_dict
            differences in values of shared keys between self.flat_dict and reference_dict
        """
        if isinstance(reference_dict, dict):
            flattened_reference_dict = self.__flatten_dict(reference_dict)
        elif isinstance(reference_dict, FlatDict):
            flattened_reference_dict = reference_dict
        else:
            raise ValueError('Provided object is not an instance of dict or FlatDict')
        key_diff_dict = []
        for key in list(self.flat_dict):
            if key not in flattened_reference_dict:
                key_diff_dict.append(key)
                self.flat_dict.pop(key, None)
        key_diff_reference_dict = []
        for key in list(reference_dict):
            if key not in self.flat_dict:
                key_diff_reference_dict.append(key)
                self.flat_dict.pop(key, None)
        values_diff = self.diff(reference_dict)

        return key_diff_dict, key_diff_reference_dict, values_diff

    def include_dict(self, reference_dict):
        """
        include_dict check if the passed on dictionnary items are all present in self.

        Args:
            reference_dict (dict or flat_dict): A dict or flat_dict instance.

        Raises:
            ValueError: when the provided reference_dict isn't an instance of FlatDict ou dict.

        Returns:
            (boolean): True if all the items in refence_dict are present in self, False otherwise.
        """
        include = True
        if isinstance(reference_dict, dict):
            flattened_reference_dict = self.__flatten_dict(reference_dict)
        elif isinstance(reference_dict, FlatDict):
            flattened_reference_dict = reference_dict
        else:
            raise ValueError('Provided object is not an instance of dict or FlatDict')
        for key in flattened_reference_dict:
            if key not in self.flat_dict:
                include = False
            elif self.flat_dict[key] != flattened_reference_dict[key]:
                include = False
        return include

def main():

    payload_params = {
        'label': 'valeur de label',
        'name': 'valeur de name',
        'network': {
            'src_ip_addr': 'valeur de src_ip_addr',
            'src_udp_port': 'valeur de src_udp_port',
            'dst_ip_addr': 'valeur de dst_ip_addr',
            'dst_udp_port': 'valeur de dst_udp_port',
            'dst_mac': 'valeur de dst_mac',
            'vlan_tag': 'valeur de vlan_tag',
            'enable': 'valeur de enable'
            },
        'format': {
            'aud_chan_map': 'valeur de aud_chan_map',
            'mapping': {
                # 'ch0': 'channel_0',
                # 'ch1': 'channel_1'
                'ch0': {
                    'x1': "X1",
                    'x2': "X2"
                    },
                'ch1': {
                    'y1': "Y1",
                    'y2': "Y2"
                    }
                },
            'aud_ptime_idx': 'valeur de aud_ptime_idx'
            }
    }

    d2 = {
        'label': 'valeur de label',
        'name': 'valeur de name',
        'network': {
            'src_ip_addr': 'valeur de src_ip_addr',
            'vlan_tag': 'valeur de vlan_tag',
            'enable': 'valeur de enable'
            },
        'format': {
            'aud_chan_map': 'valeur de aud_chan_map',
            'mapping': {
                # 'ch0': 'channel_0',
                # 'ch1': 'channel_1'
                'ch0': {
                    'x1': "X1",
                    },
                'ch1': {
                    'y2': "Y2"
                    }
                },
            'aud_ptime_idx': 'valeur de aud_ptime_idx'
            }
    }

    flat_payload = FlatDict(payload_params)

    pprint(flat_payload.include_dict(d2))
    # pprint(flat_payload)
    # print("\n")
    # unflat_payload = flat_payload.unflatten()
    # pprint(unflat_payload)

if __name__ == "__main__":
    main()