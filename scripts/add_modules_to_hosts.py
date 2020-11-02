#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address,IPv4Network
import sys, yaml
from module_utils.utils import clean_ip

def main(ip_csv, flows_csv, host_file):
    ip = ip_csv.split("\n")
    flows = flows_csv.split("\n")
    ips = []
    hostnames = []
    ip_type = []

    with open(host_file, 'r') as f:
        hosts = yaml.safe_load(f)
    
    for x in ip[1:]:        
        x = x.split(",")
        ips.append(x[2])
        hostnames.append(x[5])

    ips_index = 0

    for x in flows[1:]:
        x = x.split(",")
        try:
            if(IPv4Address(ips[ips_index]) == IPv4Address(x[0])):
                x = x[1]
                x = x.split("_")
                ip_type.append(x[0])
                ips_index = ips_index + 1
        except:
            break
            
    for x in range(0, len(ips)):
        if(ip_type[x] == "enc"):
            if 'emsfp' in hosts['all']['children']:
                if 'children' in hosts['all']['children']['emsfp']:
                    if 'encap' in hosts['all']['children']['emsfp']['children']:
                        if 'hosts' in hosts['all']['children']['emsfp']['children']['encap']:
                            hosts['all']['children']['emsfp']['children']['encap']['hosts'].update({
                                hostnames[x]:{
                                    'ansible_host_ip': ips[x]
                                }
                            })
                        else:
                            hosts['all']['children']['emsfp']['children']['encap'].update({
                                'hosts': {
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            })
                    else:
                        hosts['all']['children']['emsfp']['children'].update({
                            'encap': {
                                'hosts': {
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            }
                        })
                else:
                    hosts['all']['children']['emsfp'].update({
                        'children': {
                            'encap': {
                                'hosts': {
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            }
                        }
                    })
            else:
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
            if 'emsfp' in hosts['all']['children']:
                if 'children' in hosts['all']['children']['emsfp']:
                    if 'decap' in hosts['all']['children']['emsfp']['children']:
                        if 'hosts' in hosts['all']['children']['emsfp']['children']['decap']:
                            hosts['all']['children']['emsfp']['children']['decap']['hosts'].update({
                                hostnames[x]:{
                                    'ansible_host_ip': ips[x]
                                }
                            })
                        else:
                            hosts['all']['children']['emsfp']['children']['decap'].update({
                                'hosts': {
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            })
                    else:
                        hosts['all']['children']['emsfp']['children'].update({
                            'decap': {
                                'hosts': {
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            }
                        })
                else:
                    hosts['all']['children']['emsfp'].update({
                        'children': {
                            'decap': {
                                'hosts': {
                                    hostnames[x]:{
                                        'ansible_host_ip': ips[x]
                                    }
                                }
                            }
                        }
                    })
            else:
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

    with open(host_file, 'w') as outfile:
        yaml.dump(hosts, outfile, default_flow_style=False)

#TODO use clean_ip from module_utils.utils
def clean_ip(ip_address):
        if ip_address is not "0.0.0.0":
            ip_address = ip_address.lstrip('0')
            ip_address = ip_address.replace('.0', '.')
            ip_address = ip_address.replace('..', '.0.')
        return ip_address


if __name__ == "__main__":
    print()
    print()
    print()
    main(sys.argv[1], sys.argv[2], sys.argv[3])