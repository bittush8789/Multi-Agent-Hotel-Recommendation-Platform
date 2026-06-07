# Production-Grade Deployment Guide: TravelMind AI on Kubernetes (Kind)

This guide walks you through deploying the TravelMind AI Multi-Agent application onto a local Kubernetes **Kind (Kubernetes in Docker)** cluster using production-grade configurations, Prometheus/Grafana monitoring, and LangSmith tracing.

---

## 📌 Prerequisites

Before you start, make sure you have the following installed on your machine:
* **Docker**: Desktop or Engine 20.10+
* **kubectl**: Kubernetes CLI matching your cluster version
* **Kind**: Kubernetes in Docker CLI (`v0.20.0` or later)
* **API Keys**:
  * Groq API Key (for LLM orchestration)
  * SerpAPI Key (for live hotel searches)
  * LangChain API Key (optional, for LLMOps observability)

---

## 🏗️ 1. Build Docker Images Locally

We use a root-level multi-stage Dockerfile to build both the frontend and backend target images.

Navigate to the project root:
```bash
# Build Backend Image
docker build --target backend -t hotel-recommendation-backend:latest .

# Build Frontend Image
docker build --target frontend -t hotel-recommendation-frontend:latest .
```

---

## ☸️ 2. Kind Cluster Creation & Configuration

Create a Kind configuration file that allows NodePort mapping so you can access the frontend, Prometheus, and Grafana from your local machine.

Save the following config as `kind-config.yaml`:
```yaml
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30501
        hostPort: 8501
        protocol: TCP
      - containerPort: 30030
        hostPort: 3030
        protocol: TCP
      - containerPort: 30090
        hostPort: 9090
        protocol: TCP
```

Create the cluster using the configuration:
```bash
kind create cluster --name hotel-ai-cluster --config kind-config.yaml
```

Verify kubectl is pointed to the new Kind cluster:
```bash
kubectl cluster-info --context kind-hotel-ai-cluster
```

---

## 🚚 3. Load Images into Kind

Kind does not download images from external registries. You must load your local built images into the cluster nodes:

```bash
kind load docker-image hotel-recommendation-backend:latest --name hotel-ai-cluster
kind load docker-image hotel-recommendation-frontend:latest --name hotel-ai-cluster
```

---

## 🚀 4. Deploy Manifests to Kubernetes

### Step 4.1: Apply Secret Keys
Before deploying, encode your real API keys in base64:
```bash
echo -n "YOUR_API_KEY" | base64
```
Update [k8s/secrets.yaml](../k8s/secrets.yaml) with these base64-encoded strings, then run:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
```

### Step 4.2: Deploy ChromaDB Service
```bash
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/chromadb-deployment.yaml
kubectl apply -f k8s/chromadb-service.yaml
```

### Step 4.3: Deploy Application Components
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/network-policy.yaml
```

### Step 4.4: Deploy Observability (Prometheus & Grafana)
```bash
kubectl apply -f monitoring/prometheus.yaml
kubectl apply -f monitoring/grafana.yaml
```

---

## 🔍 5. Verification & Testing

### Verify Pods Status
Ensure all pods in the `hotel-ai` namespace are running:
```bash
kubectl get pods -n hotel-ai
```

### Verify Services
Check the exposed ports:
```bash
kubectl get svc -n hotel-ai
```

---

## 🔌 6. Accessing the Applications

Because of the Port Mapping configurations in our Kind cluster, you can access the applications directly via your localhost:

* **Streamlit UI**: [http://localhost:8501](http://localhost:8501)
* **FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) (requires port forwarding: `kubectl port-forward svc/backend-service 8000:8000 -n hotel-ai`)
* **Prometheus Metrics**: [http://localhost:9090](http://localhost:9090)
* **Grafana Dashboard**: [http://localhost:3030](http://localhost:3030) (Default user: `admin`, Password: `admin`)

---

## 🛠️ 7. Troubleshooting

* **Backend Pod ImagePullBackOff**: Ensure `imagePullPolicy: IfNotPresent` is set and you loaded the image into Kind using `kind load docker-image`.
* **Database Connection Issues**: If the backend cannot find ChromaDB, check the ConfigMap `CHROMA_HOST` to make sure it matches the ChromaDB service name (`chromadb-service`). Check logs:
  ```bash
  kubectl logs deployment/backend-deployment -n hotel-ai
  ```
* **Metrics Not Showing**: Ensure the FastAPI server is successfully initialized. Visit [http://localhost:8000/metrics](http://localhost:8000/metrics) via port forwarding to verify FastAPI metrics export.

---

## 🧹 8. Cleanup

To destroy the cluster and clean up all resources:
```bash
kind delete cluster --name hotel-ai-cluster
```
