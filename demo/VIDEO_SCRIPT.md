# Video script (about 10-12 minutes)

Record with Cmd+Shift+5 (screen + microphone). Save as `demo/presentation.mp4`.
Lines in *italics* are what to say. `code blocks` are what to run or open.

## Before you hit record
- Repo pushed to GitHub, Actions run green, GHCR packages public.
- Terminal tabs ready in the repo root. Browser tabs open: GitHub repo, Actions, AWS Console (region ap-south-1: VPC and EKS), ArgoCD, Prometheus, Grafana.
- Port-forwards running (run each in its own terminal):
```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80
kubectl port-forward -n argocd svc/argocd-server 8443:443
```
- ArgoCD password: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d`

## 1. Slides (about 2 min) - open demo/presentation.pptx
*Hi, I am <your name>. This is my DevSecOps capstone: a Reading List app where you add books, mark them to-read, reading or finished, and rate them.*
*Stack: FastAPI backend, React frontend, PostgreSQL. Alembic handles migrations.*
*Architecture: the browser hits an Ingress. Slash goes to the frontend, slash api goes to the backend, which talks to PostgreSQL. The backend exposes metrics that Prometheus scrapes and Grafana shows.*
*CI/CD: a push to main runs pytest, builds the frontend, builds Docker images, scans them with Trivy, and pushes them to GHCR tagged with the commit SHA. Then the pipeline updates the Helm values and ArgoCD deploys.*
*Terraform builds the VPC and EKS cluster. Key learnings: gate images with tests and scans, use immutable SHA tags, and destroy cloud resources after a demo.*

## 2. Codebase (about 1.5 min)
```bash
tree -L 2 -I 'node_modules|.venv|dist|__pycache__'
```
*backend/app has models, schemas, routes and the main file with the metrics middleware. alembic/versions has the migration. tests has 8 pytest tests that use an in-memory SQLite database, never the real one.*
*Both Dockerfiles run as non-root users, and the frontend uses a multi-stage build with Node and then Nginx.*
```bash
cd backend && pytest -v && cd ..
docker compose up --build -d     # then open http://localhost:3000, add a book
```

## 3. CI/CD (about 2 min)
```bash
git commit --allow-empty -m "Demo: trigger pipeline" && git push
```
Open GitHub, then Actions, then the running workflow.
*Test and frontend build run first. Then each image is built, scanned by Trivy, and only pushed if no HIGH or CRITICAL issues are found.* Click the Trivy step and read the result. *<Explain: Trivy scanned the OS packages and Python or Node dependencies. Result: clean / found X, which means Y.>*
Show the GHCR package page: *images are tagged with the commit SHA, never latest.*

## 4. Terraform (about 2 min)
```bash
cd terraform && terraform plan | tail -20
```
*The plan creates 54 resources: a VPC with public and private subnets, a NAT gateway, an EKS cluster and a managed node group.*
Switch to the AWS Console: show VPC (subnets) and EKS (cluster Active, node group). Mention terraform destroy at the end.

## 5. ArgoCD (about 1 min)
Open https://localhost:8443. *The application is Synced and Healthy. ArgoCD watches the Helm chart in Git. When the pipeline updates the image tag, ArgoCD deploys it automatically.*

## 6. Kubernetes (about 1 min)
```bash
kubectl get pods -n readinglist
kubectl get svc -n readinglist
kubectl get ingress -n readinglist
helm list -n readinglist
```
*Two backend and two frontend replicas, all Running. ClusterIP services. The Ingress routes slash to the frontend and slash api to the backend.* Open the app through the ingress URL.

## 7. Prometheus (about 40 s)
Open http://localhost:9090/targets. *The backend targets are UP.* Optionally curl `/metrics`.

## 8. Grafana (about 40 s)
Open http://localhost:3001 (admin / admin), then the Reading List API dashboard. Click around the app first to generate traffic. *Panels show request rate, p95 latency, 5xx errors and status codes.*

## 9. Wrap up (15 s)
*That is the full pipeline from commit to monitored deployment. Thanks for watching.*
Then run `terraform destroy` AFTER recording to stop AWS charges.
