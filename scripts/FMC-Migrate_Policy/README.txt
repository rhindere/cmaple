# Created on May 20, 2018
#
# @author: rhindere@cisco.com
#
# Copyright (c) 2018, 2019 Cisco and/or its affiliates.
#
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.0 (the "License"). You may obtain a copy of the
# License at
#
#               https://developer.cisco.com/docs/licenses
#
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

cmaple_cli
==========
!!! This application is NOT supported by Cisco - Use at your own risk !!!

Introduction
============
cmaple_cli is a macro substitution interface for the CMAPLE package.

CMAPLE - Cisco Multipurpose API Programming Language Extension
	CMAPLE is designed to provide a high level interface to all Cisco APIs
	Currently FMC, Threatgrid and AMP supported with the rest in development.
	Source code and documentation for CMAPLE can be found here:
		https://github.com/rhindere/cmaple
	CMAPLE is currently considered Alpha for testing.

Usage:
======

Unzip into a directory on your mac or windows systems with write permissions.

Notes:
------
1.	The migration tool will move anything accessible and CREATABLE through the API.
2.	The discover_fmc.operations file has a section will things to discover from the source.  
	By default, access and nat policies will be discovered.  Any dependent objects for either of those will be migrated.
3.	If you want to migrate other objects not assigned to policies, remove the # sign for the respective object.
	Note, if you uncomment some objects like “applications” it will take a long time to process them as there are over 3200 built-ins.
4.	If an object cannot be created via the current API (like an IPS or File policy):
	a.	If it doesn’t exist on the target, it will be removed from the policy 
		(i.e. access policy with custom IPS policy will not have an IPS policy assigned when migrated)
	b.	If it exists on the target, it will be assigned to the respective policy
		(i.e. if you have a custom IPS policy on the source, if an IPS policy of the same name exists on the target, it will be assigned to the access policy)
	c.	Built in IPS and other policies will be assigned no problem, just the custom stuff needs to exist.
5.	If you want interface and zone objects to be mapped to the physical interface/device, a device of the 
	same name with the same physical interface needs to exist on the target.
	a.	If a device does not exist on the target, the interface and zone objects will still be created but not mapped to the interface.
	b.	If “a”, you will need to manually map the interfaces in the objects and assign to device interfaces.
	c.	Policies will be created correctly with interface object assignments regardless of target device.
6.	Also note that api calls will create an audit log entry.  You may want to reduce the audit log limit or your thin provisioned VMs might grow disk fairly quick.
7.	You can run the migrate process repeatedly without clearing the target. Anything existing will be left alone.
	However, due to the way the NAT API model is structured and enumerated, nat policies will be duplicated on each run.  Will have a work around for this soon.


Windows and Mac Users:
----------------------
1.	Modify cmaple_cli_parameters.parameters file to change the user and password.  
	If both the source and destination fmc have the same user/password, you just need to change it here.  
	Alternatively, you can modify the username and password in the operations files discussed next if they are different for each system.
	If you don't want to hardcode the username and password, you can pass on the command line with the parameters "-rest_admin_user" and "-rest_admin_password".
2.	Modify the discover_fmc.operations and migrate_fmc.operations files to reflect the ip/port info for each system respectively.
3.	Run the cmaple_discover_fmc_policies to discover policies on the source fmc and the cmaple_migrate_fmc_policies to migrate.
	a.	Windows users can use the respective batch files or examine the batch files for syntax
	b.	Mac users can use the respective .sh files (chmod +x both the mac_cmaple_cli and both .sh files) or examine the files for syntax
