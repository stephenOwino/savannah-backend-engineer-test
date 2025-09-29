# Kubernetes Deployment for Savannah Assess API

This directory contains Kubernetes manifests to deploy the Django REST API for the Savannah Informatics Backend Engineer Assessment.

## Prerequisites

1. **Kubernetes Cluster**: Running cluster (minikube, k3s, EKS, GKE, etc.)
2. **kubectl**: Configured to connect to your cluster
3. **Ingress Controller**: NGINX Ingress Controller (optional, for external access)
4. **Docker Image**: Build and push the application image to a registry

## Quick Start

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -t savannah_assess:v2 .

# Tag for your registry (replace with your registry)
docker tag savannah_assess:v2 your-registry/savannah_assess:v2

# Push to registry
docker push your-registry/savannah_assess:v2
```

### 2. Update Image Reference

Update the image reference in `k8s/django-app.yaml` to point to your registry:

```yaml
image: your-registry/savannah_assess:v2
```

### 3. Deploy to Kubernetes

```bash
# Apply all manifests in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-pv.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/django-app.yaml
kubectl apply -f k8s/django-service.yaml

# Optional: Apply Ingress (requires NGINX Ingress Controller)
kubectl apply -f k8s/ingress.yaml
```

Or apply all at once:

```bash
kubectl apply -f k8s/
```

### 4. Verify Deployment

```bash
# Check namespace
kubectl get namespaces

# Check all resources in namespace
kubectl get all -n savannah-assess

# Check pods status
kubectl get pods -n savannah-assess

# Check logs
kubectl logs -n savannah-assess deployment/django-app-deployment
kubectl logs -n savannah-assess deployment/postgres-deployment
```

## Access the Application

### Option 1: NodePort Service (No Ingress Controller needed)

The application is exposed via NodePort on port 30800:

```bash
# Get node IP
kubectl get nodes -o wide

# Access application
http://<NODE_IP>:30800
```

### Option 2: Ingress (Requires NGINX Ingress Controller)

1. **Install NGINX Ingress Controller** (if not already installed):

   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

2. **Add host entry** to your `/etc/hosts`:

   ```bash
   echo "$(kubectl get ingress -n savannah-assess django-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}') savannah-assess.local" >> /etc/hosts
   ```

3. **Access application**:
   ```bash
   http://savannah-assess.local
   ```

### Option 3: Port Forward (Development)

```bash
kubectl port-forward -n savannah-assess service/django-app-service 8000:8000
```

Then access: http://localhost:8000

## Default Admin Credentials

The deployment automatically creates a Django superuser with the following credentials:

- **Username**: admin
- **Email**: admin@savannah.local
- **Password**: admin123

Access the admin panel at: http://localhost:8000/admin/

> **Note**: Change these credentials in production by updating the ConfigMap and Secret values.

## Environment Variables

The deployment uses ConfigMaps and Secrets to manage environment variables:

### ConfigMap (`configmap.yaml`):

- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_HOST`: Database host (service name)
- `DB_PORT`: Database port
- `DEBUG`: Django debug mode
- `ALLOWED_HOSTS`: Allowed hosts
- `DJANGO_SUPERUSER_USERNAME`: Admin username
- `DJANGO_SUPERUSER_EMAIL`: Admin email

### Secret (`secret.yaml`):

- `DB_PASSWORD`: Database password (base64 encoded)
- `DJANGO_SECRET_KEY`: Django secret key (base64 encoded)
- `POSTGRES_PASSWORD`: PostgreSQL password (base64 encoded)
- `DJANGO_SUPERUSER_PASSWORD`: Admin password (base64 encoded)

## Scaling

Scale the Django application:

```bash
kubectl scale deployment django-app-deployment --replicas=5 -n savannah-assess
```

## Monitoring

Check resource usage:

```bash
kubectl top pods -n savannah-assess
kubectl top nodes
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**: Ensure the image is pushed to a registry accessible by your cluster
2. **Database Connection**: Check if PostgreSQL pod is running and service is accessible
3. **Migrations**: Check init container logs for migration errors
4. **Health Check Failures**: If pods are not becoming ready, the health checks may be failing due to ALLOWED_HOSTS restrictions. The current deployment has health checks commented out for compatibility.
5. **Superuser Creation**: If the superuser creation fails, check that all environment variables (DJANGO*SUPERUSER*\*) are properly set in ConfigMap and Secret

### Useful Commands

```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n savannah-assess

# Execute into pod
kubectl exec -it <pod-name> -n savannah-assess -- /bin/bash

# Check service endpoints
kubectl get endpoints -n savannah-assess

# View events
kubectl get events -n savannah-assess --sort-by='.lastTimestamp'
```

## Cleanup

To remove all resources:

```bash
kubectl delete namespace savannah-assess
kubectl delete pv postgres-pv
```

## Production Considerations

1. **Image Registry**: Use a private registry for production
2. **Resource Limits**: Adjust CPU/memory limits based on load testing
3. **High Availability**: Use multiple replicas and anti-affinity rules
4. **Persistent Storage**: Use cloud storage classes instead of hostPath
5. **Secrets Management**: Use external secret management (e.g., AWS Secrets Manager)
6. **Monitoring**: Add Prometheus/Grafana for monitoring
7. **Backup**: Implement database backup strategy
8. **Security**: Network policies, RBAC, and security contexts
