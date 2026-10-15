# Reading List — DevSecOps Capstone

A small reading-list tracker (add books, mark them `to-read` / `reading` / `finished`, rate them) used as the vehicle for a complete DevSecOps pipeline: tests, containers, CI/CD with security scanning, Terraform-provisioned AWS EKS, Helm, ArgoCD GitOps, and Prometheus/Grafana observability.

## Architecture

```
 Browser ──► Ingress (nginx) ──► /      ──► frontend (React build served by Nginx, :8080)
                              └─► /api  ──► backend  (FastAPI, :8000) ──► PostgreSQL (StatefulSet)
                                              └─ /metrics ◄── Prometheus ──► Grafana

 git push ► GitHub Actions: pytest ► frontend build ► docker build ► Trivy ► push to GHCR (:<commit SHA>)
                         └► bumps image tag in helm/readinglist/values.yaml ► ArgoCD syncs ► EKS
 Terraform ► AWS VPC (2 public + 2 private subnets) ► EKS cluster + managed node group
```

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy, Alembic, prometheus-client |
| Database | PostgreSQL 16 |
| Frontend | React 18 + Vite, served by `nginx-unprivileged` |
| Tests | pytest (in-memory SQLite test DB) |
| Containers | Docker, Docker Compose (non-root images, multi-stage frontend) |
| CI/CD | GitHub Actions, GHCR |
| Security | Trivy image scan (fails on HIGH/CRITICAL) |
| IaC | Terraform (`terraform-aws-modules/vpc`, `.../eks`) |
| Orchestration | Kubernetes (EKS), Helm, ArgoCD |
| Observability | kube-prometheus-stack (Prometheus + Grafana) |

## Repository layout

```
backend/        FastAPI app (app/), Alembic migrations, tests/, Dockerfile
frontend/       React/Vite source, nginx.conf, multi-stage Dockerfile
docker-compose.yml
.github/workflows/ci.yml
terraform/      VPC + EKS
k8s/            namespace.yaml
helm/readinglist/   Helm chart (backend, frontend, postgres, ingress, ServiceMonitor)
argocd/application.yaml
monitoring/     Prometheus/Grafana values + dashboard ConfigMap
demo/           slide deck (+ presentation video)
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/books` | list books |
| POST | `/api/books` | create |
| GET | `/api/books/{id}` | fetch one |
| PUT | `/api/books/{id}` | update |
| DELETE | `/api/books/{id}` | delete |

## Run locally

```bash
cp .env.example .env        # optional; sensible defaults exist
docker compose up --build
```

App: http://localhost:3000 · API docs: http://localhost:8000/docs · metrics: http://localhost:8000/metrics

The backend container runs `alembic upgrade head` on start, then launches uvicorn.

Tests (no database needed):

```bash
cd backend && pip install -r requirements-dev.txt && pytest -v
```

## CI/CD (`.github/workflows/ci.yml`)

On every push to `main` (and on PRs):
1. **test-backend** — `pytest -v`; a failure stops the pipeline.
2. **build-frontend** — `npm ci && npm run build`.
3. **image** (matrix: backend, frontend) — build image, **Trivy scan** (`HIGH,CRITICAL`, `exit-code 1`), and only if clean, log in to GHCR and push `ghcr.io/<owner>/<repo>-<component>:<commit SHA>` (never `latest`).
4. **gitops-update** — writes the new SHA into `helm/readinglist/values.yaml` and commits it, which ArgoCD then deploys.

No extra secrets are needed: it uses the built-in `GITHUB_TOKEN`. Make the GHCR packages public (or add an image pull secret) so the cluster can pull them.

## Terraform (`terraform/`)

Creates a VPC (2 public + 2 private subnets across 2 AZs, one NAT gateway) and an EKS cluster with a managed node group (2 x t3.medium by default).

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit if needed; no credentials go here
aws configure                                  # or export AWS_* env vars
terraform init
terraform plan
terraform apply
$(terraform output -raw configure_kubectl)
# when finished — avoid AWS charges:
terraform destroy
```

## Kubernetes / Helm / ArgoCD

```bash
# one-time cluster add-ons
helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx -n ingress-nginx --create-namespace

kubectl apply -f k8s/namespace.yaml
helm upgrade --install readinglist helm/readinglist -n readinglist
kubectl get pods,svc,ingress -n readinglist
helm list -n readinglist
```

Backend and frontend run 2 replicas each behind ClusterIP services; the Ingress routes `/` to the frontend and `/api` to the backend.

**GitOps with ArgoCD:**

```bash
helm upgrade --install argocd argo-cd --repo https://argoproj.github.io/argo-helm -n argocd --create-namespace
kubectl apply -f argocd/application.yaml     # after setting repoURL
```

The GitHub username is already set to `Swaim-Sahay` in `helm/readinglist/values.yaml` and `argocd/application.yaml`; change it if you fork the repo.

## Observability

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml
kubectl apply -f monitoring/grafana-dashboard-configmap.yaml

kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090   # Status > Targets
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80   # admin / admin
```

The chart's `ServiceMonitor` makes Prometheus scrape the backend's `/metrics`. The "Reading List API" dashboard shows request rate, p95 latency, 5xx rate and requests by status.

## Security notes

- Both images run as non-root users; Trivy gates every build.
- `.env`, state files and `terraform.tfvars` are git-ignored. No credentials are committed.
- The Postgres password in `values.yaml` and the Grafana `admin/admin` login are demo defaults — use a secret manager/sealed secrets for anything real.

## Known limitations

- Single-replica Postgres on a PVC (no HA/backups).
- Single NAT gateway to save cost (not highly available).
- Ingress uses the controller's load balancer hostname unless `ingress.host` is set.
