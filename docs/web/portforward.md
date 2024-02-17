---
layout: post
title: Port Forwarding
image: img/thomas-jensen-ISG-rUel0Uw-unsplash.jpg
author: [chefbc]
date: 2020-11-20
draft: false
tags:
  - networking
excerpt: This is intended as a quick reference for Port Forwarding.
---

Add port forwarding from 443 to 18443 with  iptables
```bash
iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 18443
iptables -L -t nat
```


Add port forwarding from 443 to 18443 with firewalld
```bash
systemctl start firewalld
systemctl enable firewalld
firewall-cmd --add-forward-port=port=443:proto=tcp:toport=18443
firewall-cmd --runtime-to-permanent
firewall-cmd --list-all
```

Remove port forwarding from 443 to 18443 with firewalld
```bash
firewall-cmd --remove-forward-port=port=443:proto=tcp:toport=18443
firewall-cmd --runtime-to-permanent
firewall-cmd --list-all
```

### References
- https://www.liquidweb.com/kb/an-introduction-to-firewalld/
- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/sec-port_forwarding
- https://www.cyberciti.biz/faq/how-to-save-iptables-firewall-rules-permanently-on-linux/
- https://www.thegeekdiary.com/centos-rhel-how-to-make-iptable-rules-persist-across-reboots/
- https://www.systutorials.com/how-to-make-iptables-ip6tables-configurations-permanent-across-reboot-on-centos-7-linux/
- https://upcloud.com/community/tutorials/configure-iptables-centos
