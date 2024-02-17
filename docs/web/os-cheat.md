---
layout: post
title: OpenShift Cheat Sheet
image: img/andy-li-CpsTAUPoScw-unsplash.jpg
author: [chefbc]
date: 2020-11-20
draft: false
tags:
  - openshift
excerpt: This is intended as a quick reference for OpenShift commands.
---


| Login/User management        |                                          |
| ---------------------------- |----------------------------------------- |
| oc login                     |   authenticate to an openshift           |
| oc logout                    |   end the current session                |
| oc whoami                    |   show the current user context          |

```bash
oc login -u kubeadmin -p xxx https://api.crc.testing:6443
```

| Project management           |                                                       |
| ---------------------------- |------------------------------------------------------ |
| oc project                   |   show the current project context                    |
| oc get projects              |   show all project current login has access to        |
| oc status                    |   show overview of current project resources          |
| oc new-project               |   create a new project  and change to that context    |

```bash
oc create namespace peewee
oc project peewee
```

| Resource management          |                                                                |
| ---------------------------- |--------------------------------------------------------------- |
| oc new-app                   |   create a new app from source code, image, or template        |                   |
| oc new-build                 |   create a new build configuration from source code            |
| oc label                     |   add/update/remove labels from a resource                     |
| oc annotate                  |   add/update/remove annotations from a resource                |
| oc create                    |   create a new resource from filename or stdin                 |
| oc get                       |   retrieve a resource                                          |
| oc replace                   |   replace an existing resource from filename or stdin          |
| oc delete                    |   delete a resource                                            |
| oc edit                      |   modify a resource from text editor                           |
| oc describe                  |   retrieve a resource with details                             |

```bash
oc new-app https://github.com/chefbc/peewee.git
```

| Operational commands         |                                                   |
| ---------------------------- |-------------------------------------------------- |
| oc logs                      |   retrieve the logs for a resource                |
| oc rsh                       |   remote shell into a container                   |
| oc rsync                     |   copy files to or from a container               |
| oc exec                      |   execute a command in a container                |
| oc run                       |   create a deployment configuration from image    |
| oc idle                      |   scale resources to zero replicas                |

```bash
oc logs -f peewee-1-build
oc logs -f peewee-

oc get services --namespace=peewee
oc expose svc/peewee
oc get routes
```


| Operational commands         |                                                              |
| ---------------------------- |------------------------------------------------------------- |
| oc rollout                   |   manage deployments from configuration                      |
| oc rollout latest            |   start a new deployment with the latest state               |
| oc rollout undo              |   perform a rollback operation                               |
| oc rollout history           |   historical info for a deployment configuration             |
| oc rollout status            |   watch the status of a rollout until complete               |
| oc tag                       |   tag existing images into image streams                     |
| oc start-build               |   start a new build from a build configuration               |
| oc cancel-build              |   cancel a build in progress                                 |
| oc import-image              |   pull in images and tags from an external Docker registry   |
| oc scale                     |   change the number of pod replicas for a deployment         |

```bash
oc start-build peewee
```

