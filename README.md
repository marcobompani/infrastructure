# Infrastructure

This repository contain different Ansible playbooks to set up my infrastructure on Hetzner. The _provision.yml_ playbook
1) uploads the SSH public key
2) creates a firewall to allows inbound SSH connections
3) creates a server and configure it with _cloud-init_

The _cloud-init_ simply hardens the SSH configuration and set up a user called _ansible_ to connect to the host.
