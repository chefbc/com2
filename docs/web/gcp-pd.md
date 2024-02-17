---
layout: post
title: 'Format and Mount Disk on GCP Instance'
image: img/vincent-botta-wYD_wfifJVs-unsplash.jpg
author: [chefbc]
date: '2020-04-29'
tags:
  - Google Cloud 
#excerpt: My excerpt.
draft: false
---

This is intended as a quick reference and explanation of how to format and mount an [gcp-persistent-disk](https://cloud.google.com/compute/docs/disks/add-persistent-disk) to your compute engine VM instance.


### Requirements
1. Running VM instance in GCP
2. Service Account to interact with GCP disk.


### Create and attach new GCP Disk to compute instance

Available Disk Types: `pd-ssd` or `pd-standard`

```bash
INSTANCE_NAME="`hostname`"
DEVICE_NAME="new-disk"
ZONE_NAME="us-central1-b"
NEW_DISK_NAME="${INSTANCE_NAME}-${DEVICE_NAME}"
BKUP_SIZE_GB=15
DISK_TYPE="pd-ssd"

gcloud compute disks create "${NEW_DISK_NAME}" --size "${BKUP_SIZE_GB}" --zone "${ZONE_NAME}" --type "${DISK_TYPE}"
gcloud compute instances attach-disk "${INSTANCE_NAME}" --disk="${NEW_DISK_NAME}" --mode=rw --zone="${ZONE_NAME}" --device-name="${DEVICE_NAME}"
gcloud compute instances describe ${INSTANCE_NAME} --zone "${ZONE_NAME}" --format='yaml(name,disks)'
```


### Create and mount filesystem

ext4
```bash
DEVICE_ID=`ls -lart /dev/disk/by-id/google-${DEVICE_NAME}| sed 's|.*/||'`
sudo mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/${DEVICE_ID}
MNT_DIR="/mysql/bkupdisk"
mkdir -p ${MNT_DIR}
sudo mount -o nofail,noatime,nodev,defaults /dev/${DEVICE_ID} ${MNT_DIR}
```

xfs
```bash
DEVICE_ID=`ls -lart  /dev/disk/by-id/google-${DEVICE_NAME}| sed 's|.*/||'`
mkfs.xfs /dev/${DEVICE_ID}
MNT_DIR="/mysql/bkupdisk"
mkdir -p ${MNT_DIR}
sudo mount -o nofail,noatime,nodev,defaults /dev/${DEVICE_ID} ${MNT_DIR}
```

### Add disk to fstab to persist via reboot
ext4
```bash
echo UUID=`sudo blkid -s UUID -o value /dev/${DEVICE_ID}` ${MNT_DIR} ext4 discard,defaults,nofail 0 2 | sudo tee -a /etc/fstab
mount -a
```

xfs
```bash
echo UUID=`sudo blkid -s UUID -o value /dev/${DEVICE_ID}` ${MNT_DIR} xfs nofail,noatime,defaults,nodev 0 2 | tee -a /etc/fstab
mount -a
```

### Resize GCP disk
```bash
NEW_SIZE_GB=25
gcloud compute disks resize "${NEW_DISK_NAME}" --size "${NEW_SIZE_GB}" --zone "${ZONE_NAME}" --quiet
gcloud compute disks describe "${NEW_DISK_NAME}" --zone "${ZONE_NAME}"
```

### Extend filesystem on instance

ext4
```bash
resize2fs /dev/${DEVICE_ID}
```

xfs
```bash
xfs_growfs ${MNT_DIR} -D size
```


### Unmount and detach GCP disk
```bash
umount ${MNT_DIR}
gcloud compute instances detach-disk "${INSTANCE_NAME}" --disk="${NEW_DISK_NAME}" --zone="${ZONE_NAME}"
gcloud compute instances describe ${INSTANCE_NAME} --zone "${ZONE_NAME}" --format='yaml(name,disks)'
```

### Destroy GCP disk
```bash
gcloud compute disks delete "${NEW_DISK_NAME}" --zone="${ZONE_NAME}"
```

