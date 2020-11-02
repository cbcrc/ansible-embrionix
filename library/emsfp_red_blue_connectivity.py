#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
from module_utils.emsfp import EMSFP
from ansible.module_utils.basic import AnsibleModule
from module_utils.utils import clean_start_time
import sys, yaml, csv, os, datetime


ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

def get_inventory_name(inventory):
    inventory = inventory.split("/")
    try:
        inv_i = inventory.index("inventory")
        inventory = inventory[inv_i:]
        inventory[-1] = inventory[-1].replace('\']','')
        return "_".join(inventory)
    except Exception as e:
        return "_inventory"

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            hostname=dict(type='str', required=True),
            report_type=dict(type='str', required=True),
            start_time=dict(type='str', required=True)
            ),
        supports_check_mode=True
    )
    now = clean_start_time(str(module.params['start_time']))
    inventory = get_inventory_name(str(module.params['report_type']))
    filename = f"reports/{now}_{inventory}_rouge_et_bleu.csv"
    if(not os.path.exists(filename)):        
        with open(filename, 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(["Hostname", "IP_addr", "Rouge", "Bleu", "Unreachable"])
        f.close()

    emsfp = EMSFP()
    try:
        api_flows_url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/flows/"
        flows_list = emsfp.get_api_data(api_flows_url)

        red = []
        blue = []
        unreachable = []
        for flow in flows_list:
            try:
                flow_res = emsfp.get_api_data(f"{api_flows_url}{flow}")
                if("primary" in flow_res["name"]):
                    red.append(flow)
                elif("secondary" in flow_res["name"]):
                    blue.append(flow)
                else:
                    none.append(flow)
            except Exception as e:
                unreachable.append(flow)
    except Exception as e:
        with open(filename, 'a+') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow([module.params['hostname'], module.params['ip_addr'], "unreachable", "unreachable", "unreachable host"])
        f.close()
    try:
        with open(filename, 'a+') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow([module.params['hostname'], module.params['ip_addr'],None,None,None])
        f.close()
        with open(filename, 'a+') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            for x in range(0, max(len(red), len(blue), len(unreachable))):
                row = [None,None]
                if(x < len(red)):
                    row.append(red[x])
                else:
                    row.append(None)
                if(x < len(blue)):
                    row.append(blue[x])
                else:
                    row.append(None)
                if(x < len(unreachable)):
                    row.append(unreachable[x])
                else:
                    row.append(None)
                wr.writerow(row)
        f.close()
    except Exception as e:
        with open(filename,"a+") as f:
            f.write(e)
        module.fail_json(changed=False, msg=f"{e}")

    module.exit_json(changed=True, msg=f"Ok")

if __name__ == '__main__':
    main()  