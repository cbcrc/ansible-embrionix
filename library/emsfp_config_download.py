#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
from json import dump as json_dump
import yaml
from yaml import dump as yaml_dump
from requests import get, put
from module_utils.emsfp import EMSFP
from module_utils.utils import configure_em_device
from module_utils.flatdict import FlatDict
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {'metadata_version': '1.0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: 
author:
    - Société Radio-Canada
version_added: ""
short_description: Courte description
description:
    - Longue description
options:

notes:

requirements:

'''

EXAMPLES = '''
'''

RETURN = '''
status:
    description:
    returned: success
    type: complex
    contains: {
        }
'''

'''[Constantes de validation des entrées]

'''

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_addr=dict(type='str', required=True),
            config=dict(type='dict', required=False),
            key_filter=dict(type='list', default=list()),
            ignored_route_filter=dict(type='list', default=list())
            ),
        supports_check_mode=True
    )

    try:
        url = f"http://{IPv4Address(module.params['ip_addr'])}/emsfp/node/v1/"
    except (AddressValueError, NetmaskValueError) as e:
        module.fail_json(changed=False, msg=e)

    em = EMSFP(url)
    # Exit module differently base on different situation.
    if (module.check_mode == True):
        module.exit_json(changed=True, msg=f"Payload would had been sent to {module.params['ip_addr']} (check_mode)")
    else:
        em_subdict = {'module_ip':module.params['ip_addr']}
        em_subdict.update({'parameters':em.get_all_routes(key_filter=module.params['key_filter'], ignored_route_filter=module.params['ignored_route_filter'])})
        em_configuration = {'embrionix_module':em_subdict}
        # line below taken from https://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order
        yaml.add_representer(dict, lambda self, data: yaml.representer.SafeRepresenter.represent_dict(self, data.items()))
        module.exit_json(changed=True, msg=f"{yaml_dump(em_configuration, default_flow_style=False)}")

if __name__ == '__main__':
    main() 