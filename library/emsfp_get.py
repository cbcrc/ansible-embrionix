#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, Société Radio-Canada>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from ansible.module_utils.basic import AnsibleModule
import json, requests

def main():

    fields = {
        "url": {"required": True, "type": "str"}
    }

    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=True
    )

    url = module.params['url']

    try:
        response = requests.get(url)

        try:
            response = response.json()
        except:
            response = str(response)
    except requests.exceptions.HTTPError as e:
        response = str(e)

    module.exit_json(changed=False, msg=response)

if __name__ == '__main__':
    main()