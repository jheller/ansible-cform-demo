# ansible-cform-demo
Example of using Ansible to provision layered Cloudformation stacks.

A simple Ansible playbook runs a role. There is a role for each type of stack.

## network stack
This stack creates a VPC, subnets, route tables and Network ACLs.

It outputs the subnet IDs.

## database stack
This stack creates an RDS instance and a security group allowing connection to it.

It needs subnet IDs from the network stack.

It outputs the RDS DNS name and the security group ID.

## application stack
This stack creates a HA pair of EC2 instances with an ELD, and the security groups to connect them together and to the
designated database stack.

It needs subnet IDs from the network stack and the RDS DNS name and database security group ID.

## Running the playbook.
Example invocation
```
ansible-playbook -i hosts.ini -v pb-cloudformation.yml --extra-vars "cf_stack=application vpc=0 app_name=mysite"
```
Useful parameters to pass in extra-vars, and their default value if not specified.

| Parameter | Notes| Default |
|-----------|-------|--------|
| env       | Choose the account to run this is | devops |
| vpc       | VPC to use/create. IPs and subnets are automatically calculated | 0 |
| cf_stack | the stack to run | No default. Must be passed. |
| db_env | which database stack to create or use | dev |
| app_env | Which application environment to create | wordpress |
| app_name | a unique name for each application stack instance | wordpress |

## Configuring an application
Variables are loaded from sub-folders in the group_vars folder in the following order. All .yml files from  folders selected by certain variables are loaded.

| Folder | Contents |
|--------|----------|
| all | Always loaded. Defaults can be defined in here |
| 01-{{ env }} | Variable specific to the account |
| 02-{{ db_env }} | Variables that define the RDS instance. |
| 03-{{ app_env }}| Variables for the application, including EC2 parametrs and user data, and security groups. |
