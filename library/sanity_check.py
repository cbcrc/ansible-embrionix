#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
import sys, yaml, json, os, datetime
from module_utils.flatdict import FlatDict

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

def main():
    module = AnsibleModule(
        argument_spec=dict(
            current=dict(type='str', required=True),
            downloaded=dict(type='str', required=True),
            hostname=dict(type='str', required=True)
        ),
        supports_check_mode=True,
    )
    print(module.params['current'])
    hostname = module.params['hostname']
    with open(module.params['downloaded']) as x:
        downloaded = yaml.load(x, yaml.Loader)
    with open(module.params['current']) as x:
        current = yaml.load(x, yaml.Loader)

    downloaded_flat_dict = FlatDict(downloaded)
    current_float_dict = FlatDict(current)
    key_diff_down_current, key_diff_current_down, value_diff = downloaded_flat_dict.key_diff(current)

    now = datetime.datetime.now()
    if(len(key_diff_current_down) > 0 or len(key_diff_down_current) > 0 or len(value_diff) > 0):  
        with open('reports/' + hostname + '_' + now.strftime("%Y-%m-%d_%H:%M:%S") + '.txt', 'w') as f:
            print('The differences in the downloaded file: ' + module.params['downloaded'] + '\ncurrent:' + module.params['current'], file=f)

            if(len(key_diff_down_current) > 0):
                print('\nThe downloaded file contains keys that the current file doesn\'t:', file=f)
                for x in key_diff_down_current:
                    print("\t- " + str(x), file=f)
            if(len(key_diff_current_down) > 0):
                print('\nThe current file contains keys that the downloaded file doesn\'t:', file=f)
                for x in key_diff_current_down:
                    print("\t- " + str(x), file=f)
            if(len(value_diff) > 0):
                print('\nThe value differences between shared keys in the two files are:', file=f)
                for x in value_diff:
                    print("\t- " + str(x), file=f)

        module.exit_json(changed=True, msg=f"There were differences in the file {module.params['current']} and the downloaded configuration", values=[key_diff_current_down, key_diff_down_current, value_diff], default_flow_style=False)
    else:
        module.exit_json(changed=False, msg=f"Both files are the same")
                

if __name__ == '__main__':
    main()