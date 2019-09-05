#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys, yaml

def main(ip_csv, flows_csv, host_file):
    ip = ip_csv.split("\n")
    flows = flows_csv.split("\n")
    ips = []
    hostnames = []
    ip_type = []

    with open(host_file, 'r') as f:
        hosts = yaml.load(f)
    
    for x in ip[1:]:        
        x = x.split(",")
        ips.append(x[2])
        hostnames.append(x[5])
 
    ips_index = 0
    for x in flows[1:]:
        x = x.split(",")
        try:
            if(ips[ips_index] == x[0]):
                x = x[1]
                x = x.split("_")
                ip_type.append(x[0])
                ips_index = ips_index + 1
        except:
            break

    for x in range(0, len(ips)):
        if(ip_type[x] == "enc"):
            try:
                hosts['all']['children']['emsfp']['children']['encap']['hosts'].update({
                    hostnames[x]:{
                        'ansible_host_ip': ips[x]
                    }
                })
            except:
                hosts['all']['children'].update({
                    'emsfp': {
                        'children':{
                            'encap':{
                                'hosts':{
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            }
                        }
                }})
        elif(ip_type[x] == "dec"):
            try:
                hosts['all']['children']['emsfp']['children']['decap']['hosts'].update({
                    hostnames[x]:{
                        'ansible_host_ip': ips[x]
                    }
                })
            except:
                print(x)
                hosts['all']['children'].update({
                    'emsfp': {
                        'children':{
                            'decap':{
                                'hosts':{
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            }
                        }
                }}) 

    print(hosts)

    with open(host_file, 'w') as outfile:
        yaml.dump(hosts, outfile, default_flow_style=False)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])