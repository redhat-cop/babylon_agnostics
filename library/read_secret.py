#!/usr/bin/env python

# Copyright: (c) 2020, Guillaume Core <gucore@redhat.com>
from __future__ import (absolute_import, division, print_function)
import base64
import json

__metaclass__ = type

DOCUMENTATION = r'''
---
module: read_secret

short_description: This module read a k8s secret from a var and convert the base64 content to vars

version_added: "1.0.0"

description: ""

options:
    name:
        description: The var to read the secret from
        required: true
        type: str

author:
    - Guillaume Core (@fridim)
'''

EXAMPLES = r'''
# Pass in a message
- name: Read secret from OpenShift
  k8s_info:
    namespace: mynamespace
    name: mysecret
    api: v1
    kind: Secret
  register: r_secret

- name: Test with a message
  read_secret:
    secret: "{{ r_secret.resources[0] }}"
  register: r_converted

- name: Debug a secret value
  debug:
    msg: "token: {{ r_converted.data.token }}"
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_secret:
    description: The original secret
    type: dict
    returned: always
    sample: {
      'apiVersion': 'v1',
      'data': {
        'key': '...BASE64...'
        'key2': '...BASE64...'
      }
    }
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
data:
    description: The dictionary containing the converted secret data
    type: dict
    returned: always
    sample: {
        'key': 'clear'
        'key': 'clear2'
    }
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        secret=dict(type='dict', required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message='',
        my_useful_info={},
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['changed'] = False
    result['failed'] = False
    result['original_secret'] = module.params['secret']
    try:
        result['data'] = convert_data(module.params['secret']['data'])
    except Exception as err:
        result['failed'] = True
        result['messsage'] = err
        result['data'] = {}

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def convert_data(data):
    result = { k: base64.b64decode(v).decode('utf-8') for (k, v) in data.items() }

    for k, v in result.items():
        try:
            result[k] = json.loads(v)
        except json.decoder.JSONDecodeError:
            pass
    return result

def main():
    run_module()

if __name__ == '__main__':
    main()
