# Submission status vs. SUBMISSION.md / GRADING.md

Deadline: Sunday 19 Oct 2026, 11:59 PM IST. Nothing has been pushed or submitted.

## Done and verified locally

| Module | Item | Evidence |
|---|---|---|
| M1 | FastAPI, 5 CRUD endpoints + /health, Alembic migration, React UI | `docker compose up` run, see `demo/evidence/running-app-and-metrics.txt` |
| M2 | 8 pytest tests on SQLite test DB, `pytest.ini`, `conftest.py` | `demo/evidence/pytest-output.txt` |
| M3 | 13 meaningful commits, `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv` | `git log` |
| M4 | Backend Dockerfile, multi-stage frontend Dockerfile, non-root (uid 10001 / nginx 101), compose with 3 services | `demo/evidence/docker-compose-up.txt` |
| M5 / M6 | Workflow: pytest, frontend build, image build, Trivy (HIGH/CRITICAL fails), SHA-tagged GHCR push | `.github/workflows/ci.yml` (written, not yet run) |
| M7 | Terraform VPC + EKS, `tfvars.example`; `init` and `validate` pass | `demo/evidence/terraform-validate-and-helm-lint.txt` |
| M8 | `k8s/namespace.yaml`, Helm chart (2 replicas, ClusterIP, Ingress `/` and `/api`), ArgoCD Application; `helm lint` passes | same file |
| M9 | `/metrics` endpoint, ServiceMonitor, Prometheus/Grafana values, dashboard ConfigMap | `running-app-and-metrics.txt` |
| M10 | README with all required sections, 9-slide deck `demo/presentation.pptx` | files in repo |

## NOT done — I could not do these

1. **Presentation video (MP4)** — mandatory; no video = 0 for M10. I cannot record your screen/voice. You must record it following the order in SUBMISSION.md.
2. **Push to GitHub** — you said not to submit anywhere, and the repo/GHCR owner is yours. Do it yourself.
3. **GitHub Actions run, Trivy output, GHCR package page** — need the repo pushed to GitHub; I could not run Trivy locally either (blocked).
4. **`terraform plan` / `apply` / `destroy` and AWS Console proof** — need your AWS credentials and billing; I must not handle credentials, and it costs money.
5. **EKS deployment: `helm upgrade --install`, `kubectl get pods/svc`, `helm list`, Ingress in browser** — needs the live cluster from step 4.
6. **ArgoCD synced app** — needs the cluster and the pushed repo.
7. **Prometheus Targets page and Grafana live dashboard** — need the cluster.
8. **Image screenshots** (browser at localhost:3000, terminal screenshots, commit history screenshot) — I saved text outputs instead; take the screenshots yourself.
9. **Google Form submission** — not allowed/requested.

## Your checklist
1. Replace `YOUR_GITHUB_USER` in `helm/readinglist/values.yaml` and `argocd/application.yaml`.
2. Create a public GitHub repo, push `main`, confirm the Actions run is green, make GHCR packages public.
3. Follow the README: Terraform, ingress-nginx, Helm, ArgoCD, kube-prometheus-stack.
4. Take screenshots, record the video, put it in `demo/`, commit and push.
5. Run `terraform destroy`.
6. Submit at https://forms.gle/XWAP1vAumDJgAPM1A.

Also be ready to explain the project and one Trivy result yourself; the rubric awards a point for that.
