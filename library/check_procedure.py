#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule


def get_procedure(variables):
    if(variables[0]['mac_address'] == ''):
        return 'port'
    else:
        return 'mac'

def main():
    module = AnsibleModule(
        argument_spec=dict(
            variables=dict(type='list', required=True)
            ),
        supports_check_mode=True,
    )

    procedure = get_procedure(module.params['variables'])
    module.exit_json(changed=False, msg=procedure)

if __name__ == '__main__':
    main()