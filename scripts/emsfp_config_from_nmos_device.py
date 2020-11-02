#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Authors:
# * "Martin Vachon" <martin.vachon@radio-canada.ca>
# * "Patrick Keroulas" <patrick.keroulas@radio-canada.ca>
# * "Sunday Nyamweno" <sunday.nyamweno@radio-canada.ca>
#
# Ansible is typically used with the Ember+ firmware to stage devices
# using the emSFP API.  When emSFP is equipped with the Ember+ firmware,
# the flowIDs are fixed for ALL emSFP devices.  However, emSFP flow IDs
# are unique for each device when using the # *NMOS* firmware.
# Additionally, The flow IDs for a specific device change after an
# application reset.
#
# The script:
# 1)  obtains the flow IDs for 1 Video flow, first 4 audio flows
#     and 1-ANC flow, for both channels and both primary and secundary path.
# 2)  assign new values for 'label' and 'names' to reflect CBC architecture.
# 3)  sets the Aud-chan-map and aud-ptime as is typically done
#         aud-flow-1:  2ch - CH 7,8 - aud-ptime 1ms
#         aud-flow-2:  6ch - CH 1-6- aud-ptime 1ms
#         aud-flow-3:  8ch - CH 9-16- aud-ptime 0.125ms
#         aud-flow-4: 16ch - CH 1-16- aud-ptime 0.125ms
# 4)  generates output config-file.csv that can be modified further
#     before being used by a playbook.
#
# The script can be re-used after a device is configured as long as the
# Names and Labels are either default or CBC values.

import requests
import json
import sys
import csv
from requests import get

if len(sys.argv) < 2:
    print ('Usage:\n   ' + sys.argv[0] + ' <emSFP-IP>')
    exit(-1)

# This part brings the script where the info we want to collect are.
ip = sys.argv[1]
url = 'http://'+ip+'/emsfp/node/v1/flows/'
try:
    flows_response = requests.get(url).json()
except Exception as e:
    print("Could not request url: " + str(url))
    print("Details: " + str(e))
    print("First try to ping: " + str(ip))
    exit(-1)

#This part change the name of the flows for the name we want.
new_names = new_labels = [
    'SDI1-V-R',
    'SDI1-V-B',
    'SDI1-A1-R',
    'SDI1-A1-B',
    'SDI1-A2-R',
    'SDI1-A2-B',
    'SDI1-A3-R',
    'SDI1-A3-B',
    'SDI1-A4-R',
    'SDI1-A4-B',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'SDI1-Anc-R',
    'SDI1-Anc-B',
    'SDI2-V-R',
    'SDI2-V-B',
    'SDI2-A1-R',
    'SDI2-A1-B',
    'SDI2-A2-R',
    'SDI2-A2-B',
    'SDI2-A3-R',
    'SDI2-A3-B',
    'SDI2-A4-R',
    'SDI2-A4-B',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'ignored',
    'SDI2-Anc-R',
    'SDI2-Anc-B'
]

# new audio mapping
mod_aud_chan_map ={
    'tx ch1 flow 1 primary':   '00C0', # mapping with default names
    'tx ch1 flow 1 secondary': '00C0',
    'tx ch1 flow 2 primary':   '003F',
    'tx ch1 flow 2 secondary': '003F',
    'tx ch1 flow 3 primary':   'FF00',
    'tx ch1 flow 3 secondary': 'FF00',
    'tx ch1 flow 4 primary':   'FFFF',
    'tx ch1 flow 4 secondary': 'FFFF',
    'tx ch2 flow 1 primary':   '00C0',
    'tx ch2 flow 1 secondary': '00C0',
    'tx ch2 flow 2 primary':   '003F',
    'tx ch2 flow 2 secondary': '003F',
    'tx ch2 flow 3 primary':   'FF00',
    'tx ch2 flow 3 secondary': 'FF00',
    'tx ch2 flow 4 primary':   'FFFF',
    'tx ch2 flow 4 secondary': 'FFFF',
    'SDI1-A1-R': '00C0', # mapping with new CBC names
    'SDI1-A1-B': '00C0',
    'SDI1-A2-R': '003F',
    'SDI1-A2-B': '003F',
    'SDI1-A3-R': 'FF00',
    'SDI1-A3-B': 'FF00',
    'SDI1-A4-R': 'FFFF',
    'SDI1-A4-B': 'FFFF',
    'SDI2-A1-R': '00C0',
    'SDI2-A1-B': '00C0',
    'SDI2-A2-R': '003F',
    'SDI2-A2-B': '003F',
    'SDI2-A3-R': 'FF00',
    'SDI2-A3-B': 'FF00',
    'SDI2-A4-R': 'FFFF',
    'SDI2-A4-B': 'FFFF',
}

# new audio ptime
mod_aud_ptime_idx ={
    'tx ch1 flow 1 primary':   '0', # ptime with default names
    'tx ch1 flow 1 secondary': '0',
    'tx ch1 flow 2 primary':   '0',
    'tx ch1 flow 2 secondary': '0',
    'tx ch1 flow 3 primary':   '1',
    'tx ch1 flow 3 secondary': '1',
    'tx ch1 flow 4 primary':   '1',
    'tx ch1 flow 4 secondary': '1',
    'tx ch2 flow 1 primary':   '0',
    'tx ch2 flow 1 secondary': '0',
    'tx ch2 flow 2 primary':   '0',
    'tx ch2 flow 2 secondary': '0',
    'tx ch2 flow 3 primary':   '1',
    'tx ch2 flow 3 secondary': '1',
    'tx ch2 flow 4 primary':   '1',
    'tx ch2 flow 4 secondary': '1',
    'SDI1-A1-R': '0', # ptime with new CBC names
    'SDI1-A1-B': '0',
    'SDI1-A2-R': '0',
    'SDI1-A2-B': '0',
    'SDI1-A3-R': '1',
    'SDI1-A3-B': '1',
    'SDI1-A4-R': '1',
    'SDI1-A4-B': '1',
    'SDI2-A1-R': '0',
    'SDI2-A1-B': '0',
    'SDI2-A2-R': '0',
    'SDI2-A2-B': '0',
    'SDI2-A3-R': '1',
    'SDI2-A3-B': '1',
    'SDI2-A4-R': '1',
    'SDI2-A4-B': '1',
}


# This section creates an exclude list and force a value for the audio flows.
exclude_default_names = [
    'tx ch1 flow 5 primary',
    'tx ch1 flow 5 secondary',
    'tx ch1 flow 6 primary',
    'tx ch1 flow 6 secondary',
    'tx ch1 flow 7 primary',
    'tx ch1 flow 7 secondary',
    'tx ch1 flow 8 primary',
    'tx ch1 flow 8 secondary',
    'tx ch2 flow 5 primary',
    'tx ch2 flow 5 secondary',
    'tx ch2 flow 6 primary',
    'tx ch2 flow 6 secondary',
    'tx ch2 flow 7 primary',
    'tx ch2 flow 7 secondary',
    'tx ch2 flow 8 primary',
    'tx ch2 flow 8 secondary'
]

fieldnames = ['Target',
    'FlowType',
    'Flow',
    'label',
    'name',
    'src_ip_addr',
    'src_udp_port',
    'dst_ip_addr',
    'dst_udp_port',
    'dst_mac',
    'vlan_tag',
    'ssrc',
    'rtp_pt',
    'dscp',
    'enable',
    'aud_chan_map',
    'aud_ptime_idx',
    'anc_flow_profile'
]

# The script grab the info and put them in a csv file.
with open('config-file.csv', 'w') as file:
    writer = csv.DictWriter(file,fieldnames=fieldnames)
    writer.writeheader()

    for i, one_flow in enumerate (flows_response):
        # request individual flow details
        one_flow_response = get(url + one_flow).json()

        if one_flow_response['name'] in exclude_default_names:
            continue
        aud_chan_map = ''
        aud_ptime_idx = ''
        anc_flow_profile = ''

        if one_flow_response['format']['format_type'] == 'audio':
            aud_chan_map = mod_aud_chan_map[one_flow_response['name']]
            aud_ptime_idx = mod_aud_ptime_idx[one_flow_response['name']]
        if one_flow_response['format']['format_type'] == 'ancillary':
            anc_flow_profile = '0'

        row = {
             'Target': ip,'FlowType': 'enc_'+one_flow_response['format']['format_type'],
             'Flow': flows_response[i],
             'label': new_labels[i],
             'name': new_names[i],
             'src_ip_addr': one_flow_response['network']['src_ip_addr'],
             'src_udp_port': '10000',
             'dst_ip_addr': one_flow_response['network']['dst_ip_addr'],
             'dst_udp_port': '20000',
             'dst_mac': 'Aut.Gen',
             'ssrc': one_flow_response['network']['ssrc'],
             'rtp_pt': one_flow_response['network']['rtp_pt'],
             'dscp': one_flow_response['network']['dscp'],
             'enable': one_flow_response['network']['enable'],
             'aud_chan_map': aud_chan_map,
             'aud_ptime_idx': aud_ptime_idx,'anc_flow_profile': anc_flow_profile
        }
        #print(str(row))

        writer.writerow(row)

print ('Results compiled in config-file.csv file')
