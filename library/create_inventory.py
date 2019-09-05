#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys, yaml

def create_host(ip, location, name):

    data = dict(
        all = dict(
            children = dict(
                arista = dict(
                    hosts = dict(
                        arista1 = dict(
                            ansible_host = ip
                        )
                    )
                )
            )
        )
    )

    with open('embrionix/inventory/' + location + '/' + name + '/hosts.yml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

def create_group_vars(location, name):
    
    data = dict(
        ansible_connection = "network_cli",
        ansible_network_os = "eos",
        ansible_user = "{{ vault_arista_user }}",
        ansible_password = "{{ vault_arista_pass }}",
        arista_user = "{{ vault_arista_user }}",
        arista_pass = "{{ vault_arista_pass }}",
        csv_base_path = "inventory/" + location + "/" + name + "/csv",
        emsfp_csv_path = "{{ csv_base_path }}/EMSFP_data.csv",
        ipconfig_csv_path = "{{ csv_base_path }}/test_ipconfig_payload.csv",
        flow_csv_path = "{{ csv_base_path }}/modules_flow_payload.csv",
        reset_csv_path = "{{ csv_base_path }}/test_reset_payload.csv",
        sdi_audio_mapping_csv_path = "{{ csv_base_path }}/EmbrionixConfigurationCSV.csv",
        ptp_csv_path = "{{ csv_base_path }}/EmbrionicConfigurationCSV.csv"
    )

    vault_data = dict(
        vault_arista_user = "",
        vault_arista_pass = ""
    )

    with open('embrionix/inventory/' + location + '/' + name + '/group_vars/all/all.yml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

    with open('embrionix/inventory/' + location + '/' + name + '/group_vars/all/vault.yml', 'w') as outfile:
        yaml.dump(vault_data, outfile, default_flow_style=False)

if __name__ == '__main__':
    if(sys.argv[4] == 'create_host'):
        create_host(sys.argv[1], sys.argv[2], sys.argv[3])
    if(sys.argv[4] == 'create_group_vars'):
        create_group_vars(sys.argv[2], sys.argv[3])