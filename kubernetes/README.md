# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the AI System Log Detection agent.

## Files Overview

- **configmap.yaml** - Configuration variables (non-sensitive)
- **secret.yaml** - Secrets like API keys (sensitive)
- **deployment.yaml** - Deployment with pod specifications
- **service.yaml** - Service for networking
- **serviceaccount.yaml** - RBAC and service account
- **hpa.yaml** - Horizontal Pod Autoscaler (optional, for auto-scaling)

## Prerequisites

1. **Kubernetes Cluster** - Running version 1.20+
   ```bash
   kubectl version --short
   ```

2. **kubectl CLI** - Installed and configured
   ```bash
   kubectl cluster-info
   ```

3. **Docker Image** - Built and available in registry
   ```bash
   docker build -t log-agent:latest .
   # Push to registry (e.g., Docker Hub, ECR, etc.)
   docker tag log-agent:latest your-registry/log-agent:latest
   docker push your-registry/log-agent:latest
   ```

## Quick Start

### 1. Update the Secret with Your API Key

```bash
# Option A: Edit the file manually
vi kubernetes/secret.yaml
# Replace "your_cohere_api_key_here" with your actual key

# Option B: Create secret from CLI (recommended for production)
kubectl create secret generic log-agent-secret \
  --from-literal=COHERE_API_KEY=$YOUR_COHERE_API_KEY \
  --namespace=default
```

### 2. Apply ConfigMap

```bash
kubectl apply -f kubernetes/configmap.yaml
```

### 3. Apply RBAC and Service Account

```bash
kubectl apply -f kubernetes/serviceaccount.yaml
```

### 4. Apply Service

```bash
kubectl apply -f kubernetes/service.yaml
```

### 5. Apply Deployment

```bash
kubectl apply -f kubernetes/deployment.yaml
```

### 6. (Optional) Apply HPA for Auto-scaling

```bash
kubectl apply -f kubernetes/hpa.yaml
```

## Verification

### Check Deployment Status

```bash
kubectl get deployments -l app=log-agent
kubectl get pods -l app=log-agent
```

### View Pod Logs

```bash
kubectl logs -f deployment/log-agent-deployment
```

### Access the Service

```bash
# Port forward to access locally
kubectl port-forward svc/log-agent-service 8000:8000

# Then access at http://localhost:8000
curl http://localhost:8000/health
```

### Monitor Pod Events

```bash
kubectl describe pod <pod-name>
kubectl get events --sort-by='.lastTimestamp'
```

## Configuration

### Environment Variables

All environment variables are managed through:

1. **ConfigMap** (`configmap.yaml`) - Non-sensitive config
   - `LOG_FILE_PATH`
   - `LOG_API_URL`
   - `POLL_INTERVAL`
   - `DURATION`
   - `COHERE_MODEL`

2. **Secret** (`secret.yaml`) - Sensitive data
   - `COHERE_API_KEY`

### Updating Configuration

```bash
# Update ConfigMap
kubectl patch configmap log-agent-config -p '{"data":{"POLL_INTERVAL":"1.0"}}'

# Update Secret
kubectl create secret generic log-agent-secret \
  --from-literal=COHERE_API_KEY=$NEW_KEY \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to apply changes
kubectl rollout restart deployment/log-agent-deployment
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment log-agent-deployment --replicas=3
```

### Auto-scaling

If HPA is enabled, the deployment will automatically scale based on:
- CPU: 70% utilization
- Memory: 80% utilization
- Min replicas: 1
- Max replicas: 5

Check HPA status:
```bash
kubectl get hpa log-agent-hpa
kubectl describe hpa log-agent-hpa
```

## Monitoring

### View Metrics (requires Prometheus)

```bash
kubectl port-forward svc/log-agent-service 8000:8000
# Access metrics at http://localhost:8000/metrics
```

### Check Resource Usage

```bash
kubectl top nodes
kubectl top pods -l app=log-agent
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### CrashLoopBackOff

```bash
# Check logs for errors
kubectl logs <pod-name> --previous

# May be due to:
# - Missing secret (COHERE_API_KEY)
# - Invalid configuration
# - Resource constraints
```

### Image Pull Errors

```bash
# Ensure image exists and is accessible
docker image inspect your-registry/log-agent:latest

# Check image pull secrets if using private registry
kubectl get secrets
```

### Health Check Failures

```bash
# The deployment includes liveness and readiness probes
# If failing, check:
# 1. API endpoint is running
# 2. Port 8000 is accessible
# 3. Application is healthy
```

## Cleanup

```bash
# Delete deployment
kubectl delete deployment log-agent-deployment

# Delete all resources
kubectl delete -f kubernetes/

# Delete namespace (if using separate namespace)
kubectl delete namespace log-agent
```

## Production Checklist

- [ ] Cohere API key is securely stored in Secrets
- [ ] Resource requests/limits are set appropriately
- [ ] Health checks are configured
- [ ] Pod disruption budget is set
- [ ] RBAC is configured with minimal permissions
- [ ] Security context is enforced (non-root, read-only)
- [ ] HPA is enabled for scaling
- [ ] Monitoring/logging is set up
- [ ] Backup/disaster recovery plan exists
- [ ] Image is stored in secure registry

## Next Steps

1. **Set up Ingress** for external access
   ```bash
   kubectl apply -f - <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: log-agent-ingress
   spec:
     rules:
     - host: log-agent.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: log-agent-service
               port:
                 number: 8000
   EOF
   ```

2. **Set up NetworkPolicy** for security
3. **Add monitoring** with Prometheus
4. **Enable logging** with ELK/Loki
5. **Configure backup** for persistent data

## Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Deployment Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Security Best Practices](https://kubernetes.io/docs/concepts/security/)
