#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
import sys, yaml

def create_host(location, name, ip):
    data = f'''---
all:
  children:
    arista:
      hosts:
        arista1:
          ansible_host: {ip}'''

    write_host_file(data, location, name)

def create_host_embox(location, name):
    data = f'''---
all:
  children:
    emsfp:
      children:'''

    write_host_file(data, location, name)

def write_host_file(data, location, name):
    with open('embrionix/inventory/' + location + '/' + name + '/hosts.yml', 'w') as outfile:
        outfile.write(data)

def create_group_vars(location, name):
    data = f'''---
ansible_connection: network_cli
ansible_network_os: eos
ansible_user: \"{{ vault_arista_user }}\"
ansible_password: \"{{ vault_arista_pass }}\"
arista_user: \"{{ vault_arista_user }}\"
arista_pass: \"{{ vault_arista_pass }}\"
inventory_base_path: inventory/{location}/{name}
csv_base_path: inventory/{location}/{name}/csv
emsfp_csv_path: \"{{ csv_base_path }}/EMSFP_data.csv\"
ipconfig_csv_path: \"{{ csv_base_path }}/test_ipconfig_payload.csv\"
flow_csv_path: \"{{ csv_base_path }}/modules_flow_payload.csv\"
reset_csv_path: \"{{ csv_base_path }}/test_reset_payload.csv\"
sdi_audio_mapping_csv_path: \"{{ csv_base_path }}/EmbrionixConfigurationCSV.csv\"
ptp_csv_path: \"{{ csv_base_path }}/EmbrionicConfigurationCSV.csv\"'''

    write_group_vars_all(data, location, name)

def create_group_vars_embox(location, name):
    data = f'''---
csv_base_path: inventory/{location}/{name}/csv/
inventory_base_path: inventory/{location}/{name}\n
#----- refclk
emsfp_refclk_1: f2807dac-985d-11e5-8994-feff819cdc9f
emsfp_refclk_2: f3807dac-985d-11e5-8994-feff819cdc9f'''

    write_group_vars_all(data, location, name)

def write_group_vars_all(data, location, name):
    with open('embrionix/inventory/' + location + '/' + name + '/group_vars/all/all.yml', 'w') as outfile:
        outfile.write(data)

if __name__ == '__main__':
    if(sys.argv[1] == 'create_host'):
        create_host(sys.argv[2], sys.argv[3], sys.argv[4])
    elif(sys.argv[1] == 'create_host_embox'):
        create_host_embox(sys.argv[2], sys.argv[3])
    elif(sys.argv[1] == 'create_group_vars'):
        create_group_vars(sys.argv[2], sys.argv[3])
    elif(sys.argv[1] == 'create_group_vars_embox'):
        create_group_vars_embox(sys.argv[2], sys.argv[3])

    