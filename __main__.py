import os
import pulumi
import pulumi_hcloud as hcloud
import requests

config = pulumi.Config()
publicKey = config.require("publicKey")
user = config.require("user")
token = os.getenv("DUCKDNS")
subdomain = config.require("subdomain")

default = hcloud.SshKey("default", name="Marco Ubuntu", public_key=publicKey)

cloud_init = f'''
#cloud-config
users:
  - name: {user}
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - {publicKey}
packages:
  - firewalld
  - tmux
package_update: true
package_upgrade: true
runcmd:
  - systemctl enable firewalld
  - systemctl start firewalld
  - firewall-cmd --zone=public --add-port=2222/tcp
  - sed -i -e '/^\(#\|\)PermitRootLogin/s/^.*$/PermitRootLogin no/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)Port 22/s/^.*$/Port 2222/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)PasswordAuthentication/s/^.*$/PasswordAuthentication no/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)KbdInteractiveAuthentication/s/^.*$/KbdInteractiveAuthentication no/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)ChallengeResponseAuthentication/s/^.*$/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)MaxAuthTries/s/^.*$/MaxAuthTries 2/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)AllowTcpForwarding/s/^.*$/AllowTcpForwarding no/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)X11Forwarding/s/^.*$/X11Forwarding no/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)AllowAgentForwarding/s/^.*$/AllowAgentForwarding no/' /etc/ssh/sshd_config
  - sed -i -e '/^\(#\|\)AuthorizedKeysFile/s/^.*$/AuthorizedKeysFile .ssh\/authorized_keys/' /etc/ssh/sshd_config
  - sed -i '$a AllowUsers {user}' /etc/ssh/sshd_config
  - reboot
'''

# create puppet master with just IPv6 to save money
puppet_master = hcloud.Server("puppet-master",
    name="puppet-master",
    datacenter="nbg1-dc3",
    image="centos-stream-9",
    server_type="cx22",
    user_data=cloud_init,
    ssh_keys=[default.id],
    public_nets=[{
        "ipv4_enabled": False,
        "ipv6_enabled": True,
    }])
    
pulumi.export("IPv6", puppet_master.ipv6_address)
requests.get(f"https://www.duckdns.org/update?domains={subdomain}&token={token}&clear=true")
response = puppet_master.ipv6_address.apply(lambda v: requests.get(f"https://www.duckdns.org/update?domains={subdomain}&token={token}&ipv6={v}"))
pulumi.export("Duck DNS", response.text)
