---
layout: post
title: Private instances access without an bastion host on GCP
image: img/chris-buckwald-RXWgx93tz8w-unsplash.jpg
author: [chefbc]
date: 2021-01-22
draft: false
tags:
  - Google Cloud
  - iap
  - proxy
  - identity
# excerpt: Working Notes
---

Identity-Aware Proxy is a managed service that can control the access to your VM without an bastion host. 

![alt text](https://cloud.google.com/iap/images/iap-tcp-forwarding-diagram.png "iap diagram")



<!-- gcloud compute ssh virtual-machine-from-terraform \
--tunnel-through-iap 

gcloud compute ssh virtual-machine-from-terraform \
--tunnel-through-iap \
--ssh-flag="-N -L 8081:localhost:80" -->

<!-- gcloud compute ssh github-actions \
--tunnel-through-iap \
--ssh-flag="-N -L 5000:localhost:5000" -->

Enabling IAP tunneling by adding ingress firewall rule from IAP’s forwarding netblock.

For SSH access:
```bash
gcloud compute firewall-rules create allow-ssh-ingress-from-iap \
  --direction=INGRESS \
  --action=allow \
  --rules=tcp:22 \
  --source-ranges=35.235.240.0/20
```

For other protocols (PORT based on protocol):
```bash
gcloud compute firewall-rules create allow-ingress-from-iap \
  --direction=INGRESS \
  --action=allow \
  --rules=tcp:PORT \
  --source-ranges=35.235.240.0/20
  ```



IAP tunneling can be enforced via IAM permissions.  (Grant the iap.tunnelResourceAccessor role to the user):

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:EMAIL \
    --role=roles/iap.tunnelResourceAccessor
```


Access via "gcloud compute ssh" command with the “tunnel-though-iap” flag to connect to an instance.

```bash
gcloud compute ssh my-instance \
--tunnel-through-iap 
```

Access via local port forwarding.

```bash
gcloud compute ssh  my-instance \
--tunnel-through-iap \
--ssh-flag="-N -L 3306:localhost:3306"
```

### References
- https://cloud.google.com/iap/docs/using-tcp-forwarding
- https://cloud.google.com/iap/docs/tcp-forwarding-overview


<!-- 
marketplace.gcr.io/google/neo4j4:latest


https://hub.docker.com/_/neo4j

docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    neo4j

docker run -it --rm --name neo4j --publish=7474:7474 --publish=7687:7687 marketplace.gcr.io/google/neo4j4


docker run -it --rm --name neo4j --publish=7474:7474 --publish=7687:7687 marketplace.gcr.io/google/neo4j4


gcloud compute ssh neo4j --tunnel-through-iap

gcloud beta compute --project=chefbc instances create-with-container neo4j --zone=us-central1-a --machine-type=n1-standard-1 --subnet=default --no-address --metadata=google-logging-enabled=true --maintenance-policy=MIGRATE --service-account=336402568157-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --image=cos-stable-85-13310-1041-161 --image-project=cos-cloud --boot-disk-size=10GB --boot-disk-type=pd-standard --boot-disk-device-name=neo4j --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --container-image=marketplace.gcr.io/google/neo4j4 --container-restart-policy=always --labels=container-vm=cos-stable-85-13310-1041-161 --reservation-affinity=any

gcloud compute ssh  neo4j \
--tunnel-through-iap \
--ssh-flag="-N -L 7474:localhost:7474"

http://0.0.0.0:7474/browser/
 -->


