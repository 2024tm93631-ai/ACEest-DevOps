# ACEest Fitness & Gym — Assignment 2

## CI/CD Pipeline with Docker Hub, SonarQube & Kubernetes

[![CI/CD Pipeline](https://github.com/2024tm93631-ai/ACEest-DevOps/actions/workflows/main.yml/badge.svg)](https://github.com/2024tm93631-ai/ACEest-DevOps/actions)

### Docker Hub
```
docker pull bharathakash2024/aceest-fitness:latest
docker run -p 5000:5000 bharathakash2024/aceest-fitness:latest
```

### Local Setup
```bash
pip install -r requirements.txt
python app.py
```

### Run Tests
```bash
pytest test_app.py -v
```

### Kubernetes Deployments
```bash
# Standard deployment
kubectl apply -f k8s/deployment.yaml

# Blue-Green
kubectl apply -f k8s/blue-green.yaml

# Canary (80/20 traffic split)
kubectl apply -f k8s/canary.yaml

# Rolling Update
kubectl apply -f k8s/rolling-update.yaml
```

### Deployment Strategies
| Strategy | File | Description |
|----------|------|-------------|
| Standard | k8s/deployment.yaml | 2 replicas, NodePort |
| Blue-Green | k8s/blue-green.yaml | Switch between v2/v3 |
| Canary | k8s/canary.yaml | 80% stable, 20% new |
| Rolling | k8s/rolling-update.yaml | Zero-downtime update |
