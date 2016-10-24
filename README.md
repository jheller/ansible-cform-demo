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
This stack creates a HA pair of EC2 instances with an ELB, and the security groups to connect them together and to the
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
| db_env | which database stack to create or use | mysql |
| db_name | A unique name for each databasse environment instance | dev|
| app_env | Which application environment to create | wordpress |
| app_name | a unique name for each application stack instance | mysite |
To stand up a full application, you need all of those variables. If they are not passed, then the defaults will be used.

Multiple instances of network, database and application stacks can co-exist. They are cross-linked by using the names of existing lower layer stacks when creating a new one.

## Configuring an application
Variables are loaded from sub-folders in the group_vars folder in the following order. All \*.yml files from  folders selected by tne *env* variables are loaded.

| Folder | Contents |
|--------|----------|
| all | Always loaded. Defaults can be defined in here |
| 01-{{ env }} | Variables specific to the account |
| 02-{{ db_env }} | Variables that define the RDS instance(s). |
| 03-{{ app_env }}| Variables for the application, including EC2 parameters and user data, plus security groups. |
