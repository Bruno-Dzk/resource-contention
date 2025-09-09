# How to deploy

1. Deploy the prometheus operator
```
kubectl create -k prom_operator
```
2. Deploy RBAC permissions
```
kubectl apply -f prom_rbac.yaml
```
3. Deploy Prometheus to the cluster
```
kubectl apply -f prometheus.yaml
```

## Local development
To forward the port:
```
kubectl port-forward svc/prometheus 9090
```
Then access prometheus in the browser: `localhost:9090`