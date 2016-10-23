#!/usr/bin/python

# This custom module returns a stack's outputs

DOCUMENTATION = '''
---
module: describe_stack
short_description: Gets the outputs of an existing AWS CloudFormation stack
description:
         - Gets the outputs of an existing AWS CloudFormation stack.
         - Fails if stack is in a faulure or in-progress state.
         - Will not fail if fail_mode is false anf stack does not exist.
options:
    stack_name:
        description:
            - name of the cloudformation stack
        required: true
    fail_mode:
        description:
            - when false, succeeds but sets no_stack to true.
            - Always fails when stack exists but is in a failure state.
        default: true
outputs:
    no_stack:
        description:
            - Boolean, set to true if there is no stack of the passed name.
    stack_outputs:
        description:
            - dictionary of stack outputs
'''

import datetime
import sys
import json
import os
import shlex

# Stack status values for a viable stack.
SUCCESS_STATES = [
    'CREATE_COMPLETE',
    'UPDATE_COMPLETE',
    'UPDATE_ROLLBACK_COMPLETE',
    'NO_STACK'
]

try:
    import boto.cloudformation.connection
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            stack_name  = dict(required=True),
            fail_mode   = dict(default=True, choices=BOOLEANS, type='bool'),
            region      = dict(default='ap-southeast-2')
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec
    )

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    stack_name = module.params['stack_name']
    fail_mode = module.params['fail_mode']

    region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module)

    try:
        conn = boto.cloudformation.connect_to_region(region, **aws_connect_kwargs)

    except boto.exception.NoAuthHandlerFound, e:
        module.fail_json(msg=str(e))

    outputs = {}
    stack_status = 'NO_STACK'

    try:
        stacks = conn.describe_stacks(stack_name)

        if len(stacks) == 1:
            no_stack = False
            msg = "stack found"

            stack = stacks[0]
            for output in stack.outputs:
                outputs[output.key] = output.value
            stack_status = stack.stack_status

    except boto.exception.BotoServerError:
        no_stack = True
        msg = "no stack named " + stack_name
        if fail_mode:
            module.fail_json(
                msg      = msg,
                no_stack = no_stack
            )

    if stack_status in SUCCESS_STATES:
        module.exit_json(
            msg           = msg,
            no_stack      = no_stack,
            stack_outputs = outputs,
            stack_status  = stack_status
        )
    else:
        module.fail_json(
            msg          = msg,
            no_stack     = no_stack,
            stack_status = stack_status
        )


from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *
if __name__ == '__main__':
        main()
