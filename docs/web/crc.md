---
layout: post
title: Home Lab Setup based on Red Hat CodeReady Containers
image: img/ousa-chea-gKUC4TMhOiY-unsplash.jpg
imageCredit: Photo by [Callum Shaw](https://unsplash.com/@callumshaw)
author: [chefbc, kc]
date: 2020-11-23
draft: false
tags:
  - openshift
excerpt: 
---


This is intended as a quick reference and explanation install CRC in a home lab.

### Downloads
- Download `crc` binary from [cloud.redhat.com](https://cloud.redhat.com/openshift/install/crc/installer-provisioned) 
- Download `oc` binary from [https://github.com/openshift](https://github.com/openshift/okd/releases)


### Installation

`crc`
```bash
wget https://mirror.openshift.com/pub/openshift-v4/clients/crc/latest/crc-linux-amd64.tar.xz

tar xvf crc-linux-amd64.tar.xz
sudo mv crc-linux-1.25.0-amd64/crc /usr/local/bin
```

`oc` & `kubectl`
```bash
wget https://github.com/openshift/okd/releases/download/4.7.0-0.okd-2021-04-11-124433/openshift-client-linux-4.7.0-0.okd-2021-04-11-124433.tar.gz

tar xvf openshift-client-linux-4.7.0-0.okd-2021-04-11-124433.tar.gz 
sudo mv oc /usr/local/bin/
sudo mv kubectl /usr/local/bin/
```

Create `crc` user
```bash
useradd crc
passwd crc
usermod -aG wheel crc
```

Setup `crc`
```bash
crc setup
```

Start `oc` and provide secret from [cloud.redhat.com](https://cloud.redhat.com/openshift/install/crc/installer-provisioned) 
```bash
crc start
```

Get `crc` ip
```bash
crc ip
```

Get `crc` console
```bash
crc console
```

### Enable Remote Access 
Install `HAProxy` with dependencies
```bash
sudo dnf -y install haproxy policycoreutils-python-utils
```

Configuring the `Firewall`
```bash
sudo systemctl start firewalld
sudo firewall-cmd --add-port=80/tcp --permanent
sudo firewall-cmd --add-port=6443/tcp --permanent
sudo firewall-cmd --add-port=443/tcp --permanent
sudo systemctl restart firewalld
sudo semanage port -a -t http_port_t -p tcp 6443
```

Configure `HAProxy`
```bash
export SERVER_IP=<SERVER_IP_HERE>
export CRC_IP=<CRC_IP_HERE>
```
Backup orginal `haproxy.cfg`
```bash
sudo cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig
```

Replace contents of the `haproxy.cfg` with:
```bash
export HOST_IP=$(hostname --ip-address)
export CRC_IP=$(crc ip)
```

```bash
tee /etc/haproxy/haproxy.cfg &>/dev/null <<EOF
defaults
    mode http
    log global
    option httplog
    option  http-server-close
    option  dontlognull
    option  redispatch
    option  contstats
    retries 3
    backlog 10000
    timeout client          25s
    timeout connect          5s
    timeout server          25s
    timeout tunnel        3600s
    timeout http-keep-alive  1s
    timeout http-request    15s
    timeout queue           30s
    timeout tarpit          60s
    default-server inter 3s rise 2 fall 3
    option forwardfor

frontend apps
    bind $HOST_IP:80
    bind $HOST_IP:443
    option tcplog
    mode tcp
    default_backend apps

backend apps
    mode tcp
    balance roundrobin
    option tcp-check
    server webserver1 $CRC_IP check port 80

frontend api
    bind $HOST_IP:6443
    option tcplog
    mode tcp
    default_backend api

backend api
    mode tcp
    balance roundrobin
    option tcp-check
    server webserver1 $CRC_IP:6443 check port 6443
EOF
```

Start and Enable `HAProxy`
```bash
systemctl start haproxy
systemctl enable haproxy.service 
```


### Configuring DNS for Client
Add line to `/etc/hosts` and replace `<SERVER_IP>` with ip of `crc` machine. 
```bash
<SERVER_IP> api.crc.testing oauth-openshift.apps-crc.testing console-openshift-console.apps-crc.testing default-route-openshift-image-registry.apps-crc.testing
```

### Access
Login with `oc` or via [web console](https://console-openshift-console.apps-crc.testing/dashboards)
```bash
oc login -u kubeadmin -p https://api.crc.testing:6443
```

### References
- https://cloud.redhat.com/openshift/install/crc/installer-provisioned
- https://www.openshift.com/blog/accessing-codeready-containers-on-a-remote-server/
- https://itnext.io/how-to-access-your-app-behind-an-openshift-router-87cbae3e7185
- https://www.linkedin.com/pulse/setup-openshift-codeready-remote-server-adrian-gigante/?articleId=6660205880115638272
- https://gist.github.com/tmckayus/8e843f90c44ac841d0673434c7de0c6a
- https://www.stevenrombauts.be/2018/01/use-dnsmasq-instead-of-etc-hosts/
- https://www.jeffgeerling.com/blog/2019/trying-out-crc-code-ready-containers-run-openshift-4x-locally
