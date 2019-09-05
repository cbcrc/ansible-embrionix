#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""[This function take a dict and flattens it]

Returns:
    [dict] -- [Returns the flattened dict]
"""
def flatten_dict(base_dict):
    flattened_dict = {}
    for key in base_dict.keys():
        if isinstance(base_dict[key], dict):
            flattened_dict.update(flatten_dict(base_dict[key]))
        else:
            flattened_dict.update({key:base_dict[key]})
    return flattened_dict

def clean_ip(ip_address):
    if ip_address is not "0.0.0.0":
        ip_address = ip_address.lstrip('0')
        ip_address = ip_address.replace('.0', '.')
        ip_address = ip_address.replace('..', '.0.')
    return ip_address