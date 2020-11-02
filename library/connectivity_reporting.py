#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
from module_utils.emsfp import EMSFP
import sys, yaml, json, os, datetime, csv
from module_utils.flatdict import FlatDict
from module_utils.utils import clean_start_time

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

def compare(reachable, all_hosts):
    for r in reachable:
        if r in all_hosts:
            all_hosts.remove(r)
    return all_hosts

def clean_all_hosts(all_hosts):
    clean = []
    for x in all_hosts:
        if ',' not in x:
            clean.append(x)
    return clean

def write_csv(reachable, all_hosts, report_type, now):
    filename = f"reports/{now}_{report_type}.csv"
    with open(filename, 'a') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(["Reachable", "Unreachable"])
        for x in range(0, max(len(reachable), len(all_hosts))):
            row = []
            if(x < len(reachable)):
                row.append(reachable[x])
            else:
                row.append(None)
            if(x < len(all_hosts)):
                row.append(all_hosts[x])
            else:
                row.append(None)
            wr.writerow(row)

def write_csv_api(reachable, all_hosts, hostvars, report_type, now, groups):
    filename = f"reports/{now}_{report_type}_api.csv"
    with open(filename, 'a') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(["Hostname", "Ip", "Ping", "Api", "Device Type"])
        for x in range(0, len(reachable)):
            row = []
            row.append(reachable[x])
            row.append(hostvars[reachable[x]]["ansible_host_ip"])
            row.append("True")

            if(check_api(hostvars[reachable[x]]["ansible_host_ip"])):
                row.append("True")    
            else:
                row.append("False")   

            row.append(get_device_type(reachable[x], groups))
            
            wr.writerow(row)
        for x in range(0, len(all_hosts)):
        
            row = []
            row.append(all_hosts[x])
            try:
                row.append(hostvars[all_hosts[x]]["ansible_host"])
            except Exception as e:
                row.append(None)
            row.append("False")

            try:
                if(check_api(hostvars[all_hosts[x]]["ansible_host"])):
                    row.append("True")    
                else:
                    row.append("False")   
            except Exception as e:
                row.append(None)
            
            wr.writerow(row)

def get_device_type(hostname, groups):
    skip_keys = ["all", "emsfp", "reachable_hosts", "unreachable_hosts"]
    for key in groups:
        if hostname in groups[key] and key not in skip_keys:
            return key
    return "No Type Found"

def check_api(ip):
    emsfp = EMSFP()
    try:
        api_url = f"http://{IPv4Address(ip)}/emsfp/node/v1/"
        res = emsfp.get_api_data(api_url)

        if('self/' in res):
            return True
        else:
            return False

    except Exception as e:
        return False

def get_inventory_name(inventory):
    inventory = inventory.split("/")
    try:
        inv_i = inventory.index("inventory")
        inventory = inventory[inv_i:]
        inventory[-1] = inventory[-1].replace('\']','')
        return "_".join(inventory)
    except Exception as e:
        return "inventory"

def main():
    module = AnsibleModule(
        argument_spec=dict(
            reachable=dict(type='list', required=True),
            all_hosts=dict(type='list', required=True),
            report_type=dict(type='list', required=True),
            start_time=dict(type='str', required=True),
            hostvars=dict(type='dict', required=False),
            device_type=dict(type='dict', required=False),
            use_api=dict(type='str', required=True)
        ),
        supports_check_mode=True,
    )

    now = clean_start_time(str(module.params['start_time']))
    inventory = get_inventory_name(str(module.params['report_type']))
    all_hosts = compare(module.params['reachable'], module.params['all_hosts'])
    all_hosts = clean_all_hosts(all_hosts)

    if(module.params['use_api'] == "yes"):
        write_csv_api(module.params['reachable'], all_hosts, module.params['hostvars'], inventory, now, module.params['device_type'])
    else:
        write_csv(module.params['reachable'], all_hosts, inventory, now)
       
    module.exit_json(changed=True, msg=f"{all_hosts}")
    
                

if __name__ == '__main__':
    main()