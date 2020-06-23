#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
import json

def main():

    module = AnsibleModule(
        argument_spec=dict(
            Target=dict(required=True, type=str),
            Flow=dict(required=True, type=str),
            FlowType=dict(required=True, type=str), 
        ),
        supports_check_mode=True
    )

    flag_payload_validity = True
    for key, value in module.params.items():
        if value == "":
            flag_payload_validity = False
    if flag_payload_validity == True:
        module.exit_json(changed=False, payload_validity=True)
    else :
        module.exit_json(changed=False, payload_validity=False)


if __name__ == '__main__':
    main()