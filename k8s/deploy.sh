#!/bin/bash

set -e

echo "Deploying Savannah Assess API to Kubernetes..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Not connected to a Kubernetes cluster"
    exit 1
fi

print_status "Connected to cluster: $(kubectl config current-context)"

# Build and tag Docker image
print_status "Building Docker image..."
docker build -t savannah_assess:v2 ..

# Apply Kubernetes manifests
print_status "Creating namespace..."
kubectl apply -f namespace.yaml

print_status "Creating secrets..."
kubectl apply -f secret.yaml

print_status "Creating config maps..."
kubectl apply -f configmap.yaml

print_status "Creating persistent volumes..."
kubectl apply -f postgres-pv.yaml

print_status "Deploying PostgreSQL..."
kubectl apply -f postgres.yaml

print_status "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/postgres-deployment -n savannah-assess

print_status "Deploying Django application..."
kubectl apply -f django-app.yaml

print_status "Creating services..."
kubectl apply -f django-service.yaml

print_status "Waiting for Django app to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/django-app-deployment -n savannah-assess

# Optional: Apply Ingress
read -p "Do you want to apply Ingress? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating Ingress..."
    kubectl apply -f ingress.yaml
    print_warning "Make sure NGINX Ingress Controller is installed in your cluster"
    print_warning "Add 'savannah-assess.local' to your /etc/hosts file pointing to your cluster IP"
fi

print_status "Deployment completed successfully! 🎉"
echo ""
print_status "Access options:"
echo "1. NodePort: http://<NODE_IP>:30800"
echo "2. Port forward: kubectl port-forward -n savannah-assess service/django-app-service 8000:8000"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "3. Ingress: http://savannah-assess.local (after configuring /etc/hosts)"
fi

echo ""
print_status "Admin Credentials:"
echo "Username: admin"
echo "Password: admin123"
echo "Admin URL: http://localhost:8000/admin/ (when using port-forward)"

echo ""
print_status "Useful commands:"
echo "kubectl get all -n savannah-assess"
echo "kubectl logs -n savannah-assess deployment/django-app-deployment"
echo "kubectl logs -n savannah-assess deployment/postgres-deployment"
