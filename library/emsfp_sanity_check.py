#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
from module_utils.emsfp import EMSFP
import sys, yaml, json, os

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

def check(last_known, current):
    for x, y in zip(last_known.items(), current.items()):
        if(x==y):
            return True
        else:
            return False

def get_hostname(path):
    temp = path.split("/")
    return temp[len(temp)-1].split('.yml')[0]

def find_diff(a, b, differences, module=""):
    for (x,y),(i,j) in zip(a.items(), b.items()):
        if(isinstance(y,dict) and isinstance(j,dict)):
              if(len(x) == 36):
                module = x
                find_diff(y,j,differences, module)
              find_diff(y,j,differences, module)
        else:            
            if(y != j):
                differences.append({module: {x: y + ' != ' + j}})

def main():
    module = AnsibleModule(
        argument_spec=dict(
            last_known=dict(type='str', required=True),
            current=dict(type='str', required=True)
        ),
        supports_check_mode=True,
    )
    hostname = get_hostname(module.params['current'])
    with open(module.params['last_known']) as x:
        last_known = yaml.load(x)
    with open(module.params['current']) as x:
        current = yaml.load(x)

    equal = check(last_known, current)
    if(equal is False):  
        differences = []
        find_diff(last_known, current, differences)
        with open('reports/report_' + hostname + '.txt', 'w') as f:
            print('The differences in the last known and current:\n' + module.params['current'] + '\n' + module.params['last_known'], file=f)
            for x in differences:
                print(str(x), file=f)

        module.exit_json(changed=True, msg=f"There were differences in the file {module.params['current']} and the last known good configuration", values=differences, default_flow_style=False)
    else:
        module.exit_json(changed=False, msg=f"Both files are the same")
                

if __name__ == '__main__':
    main()