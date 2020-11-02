#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address
import yaml

from ansible.module_utils.basic import AnsibleModule
from module_utils.utils import get_module_type2

def update_inventory(modules, inventory_path):

    with open(inventory_path + "/hosts.yml", 'r') as f:
        hosts = yaml.safe_load(f)
    
    for module in modules:        

        if 'ip_addr' in module:
            host_ip = str(IPv4Address(module['ip_addr']))
        elif 'ip_addr_red' in module:
            host_ip = str(IPv4Address(module['ip_addr_red']))
        else:
            raise KeyError("No ip assigned to 'ip_addr' or 'ip_addr_red'")

        host_name = module['hostname']
        module_type = get_module_type2(host_ip)
        
        if module_type != 'unknown':
        # if module_type != None:
            try:
                hosts['all']['children']['emsfp']['children'][module_type]['hosts'][host_name] = {
                        'ansible_host_ip': host_ip
                    }
                continue
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                hosts['all']['children']['emsfp']['children'][module_type]['hosts'] = {
                    host_name: {
                        'ansible_host_ip': host_ip
                    }
                }
                continue
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                hosts['all']['children']['emsfp']['children'][module_type] = {
                    'hosts': {
                        host_name: {
                            'ansible_host_ip': host_ip
                        }
                    }
                }
                continue
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                hosts['all']['children']['emsfp']['children'] = {
                    module_type: {
                        'hosts': {
                            host_name: {
                                'ansible_host_ip': host_ip
                            }
                        }
                    }
                }
                continue
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                hosts['all']['children']['emsfp'] = {
                    'children': {
                        module_type: {
                            'hosts': {
                                host_name: {
                                    'ansible_host_ip': host_ip
                                }
                            }
                        }
                    }
                }
                continue
            except KeyError:
                pass
            except TypeError:
                pass

    return hosts

def main():

    module = AnsibleModule(
        argument_spec=dict(
            parsed_modules_params=dict(type=list, required=True),
            inventory_hosts_path=dict(type=str, required=True),
        ),
        supports_check_mode=True,
    )

    try:
        new_inventory = update_inventory(module.params['parsed_modules_params'], module.params['inventory_hosts_path'])
        module.exit_json(changed=True, msg=f"{yaml.dump(new_inventory, default_flow_style=False)}")
    except Exception as e:
        module.fail_json(changed=False, msg=f"Exception: {e}")


if __name__ == '__main__':
    main() 