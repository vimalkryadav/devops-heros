# Kubernetes volumes

Vimal Kumar Yadav · 24BCS10273

| Object | Purpose | Example in this lab |
| --- | --- | --- |
| `emptyDir` | Pod-local scratch space shared by its containers. It survives a container restart, but disappears when the Pod is removed. | An init container writes a message and the main container reads it in [emptydir.yaml](emptydir.yaml). |
| `hostPath` | Exposes a path on the particular node running the Pod. Placement and host permissions matter. | [hostpath.yaml](hostpath.yaml) mounts the node's `/etc/os-release` read-only. |
| PersistentVolume (PV) | Cluster-scoped storage resource with capacity, access modes and a reclaim policy. | The Minikube provisioner created a PV for the claim. |
| PersistentVolumeClaim (PVC) | Namespaced request for storage, bound to a suitable PV. A Pod refers to the claim. | [web-data](../mini-project/pvc.yaml) requests 500Mi, `ReadWriteOnce`, class `standard`. |
| StorageClass | Selects a provisioner and its storage policy. | Our `standard` class uses `k8s.io/minikube-hostpath`, immediate binding and `Delete` reclamation. |
| Dynamic provisioning | Creates backing storage in response to a claim, avoiding a manually authored PV for each request. | Applying the claim produced `pvc-e726b844-35d5-444f-86a0-b030f2ea510c`. |

The volume lifecycle and host access behavior are described in the [Kubernetes volume documentation](https://kubernetes.io/docs/concepts/storage/volumes/). The separate PV and PVC objects, binding, access modes and reclamation are covered in [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/).

```text
web-app Pod -> web-data PVC -> dynamically created PV -> Minikube node storage
```

The [recorded run](../evidence/01-storage.txt) shows the init-container message, the node's OS information, the bound claim, the class settings, and the record before and after Pod replacement. The node reported Debian 12; this is the containerized Minikube node's OS, separate from the Fedora-family host.

To repeat the volume examples after creating the namespace:

```bash
kubectl apply -f 01-kubernetes-volumes/emptydir.yaml
kubectl apply -f 01-kubernetes-volumes/hostpath.yaml
kubectl -n assignment-s13 logs emptydir-demo -c reader
kubectl -n assignment-s13 logs hostpath-demo
kubectl -n assignment-s13 get pvc
kubectl get pv
kubectl get storageclass standard -o yaml
```

`ReadWriteOnce` permits read/write mounting on one node; it does not mean only one Pod may use the volume. Our replicas share one claim because this lab runs on one Minikube node. A deployment spread across nodes needs an appropriate storage design, such as separate StatefulSet claims or a supported shared filesystem. A hostPath-backed claim does not establish multi-node durability. Deleting this lab's claim also deletes its dynamically provisioned storage because the reclaim policy is `Delete`.
