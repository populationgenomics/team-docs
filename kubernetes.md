# Kubernetes cheatsheet

In each of the commands below, the `-n` or `--namespace` option specifies the namespace to operate on.
Often this will be **default**, which is the default, or your own personal namespace if you are testing within that.

There is no environment variable to set the current namespace, but you can set it via a `kubectl` command that will record your preference in _~/.kube/config_:

```bash
# Set current namespace
kubectl config set-context --current --namespace=<namespace>

# Report which namespace is current
kubectl config view | grep namespace:
```

If the latter shows no results, there's no namespace setting so it's still the default **default**.


## Show nodes in the cluster

```bash
kubectl [-n <namespace>] get pods
```


## View logs

```bash
kubectl [-n <namespace>] logs [options] <pod>
```

Useful options include:

* `--since=6h` to show logs for the last six hours
* `--tail=10` to show the most recent 10 lines
* `-f` to show log lines as they appear, as with `tail -f`


## Log in to a node

```bash
kubectl [-n <namespace>] exec -it <pod> -- bash
```

## Restart a node

```bash
kubectl [-n <namespace>] delete pod <pod>
```

The node will be deleted and a new one started in its place.
