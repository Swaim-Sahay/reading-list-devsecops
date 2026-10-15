#!/usr/bin/env bash
# Free local stand-in for EKS: kind cluster + ingress + Helm app + Prometheus/Grafana + ArgoCD.
# Run from the repo root:  bash scripts/local-cluster-demo.sh
set -euo pipefail
CTX=kind-readinglist
K="kubectl --context $CTX"
H="helm --kube-context $CTX"
EV=demo/evidence
mkdir -p "$EV"

cat > /tmp/kind.yaml <<'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - containerPort: 80
        hostPort: 8088
EOF
kind get clusters | grep -qx readinglist || kind create cluster --name readinglist --config /tmp/kind.yaml

docker build -t rl-backend:local backend
docker build -t rl-frontend:local frontend
kind load docker-image rl-backend:local rl-frontend:local --name readinglist

$K apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/kind/deploy.yaml
$K -n ingress-nginx wait --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=240s

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo add argo https://argoproj.github.io/argo-helm >/dev/null
helm repo update >/dev/null
$H upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml --wait --timeout 10m
$K apply -f monitoring/grafana-dashboard-configmap.yaml

$K apply -f k8s/namespace.yaml
$H upgrade --install readinglist helm/readinglist -n readinglist \
  --set backend.image.repository=rl-backend --set backend.image.tag=local \
  --set frontend.image.repository=rl-frontend --set frontend.image.tag=local \
  --wait --timeout 5m

{
  echo '$ kubectl get pods -n readinglist';  $K get pods -n readinglist
  echo; echo '$ kubectl get svc -n readinglist'; $K get svc -n readinglist
  echo; echo '$ kubectl get ingress -n readinglist'; $K get ingress -n readinglist
  echo; echo '$ helm list -n readinglist'; $H list -n readinglist
} | tee "$EV/k8s-helm-output.txt"

echo; echo "App via Ingress: http://localhost:8088"
curl -s -XPOST localhost:8088/api/books -H 'Content-Type: application/json' -d '{"title":"Dune","author":"Frank Herbert"}' >/dev/null
for i in $(seq 1 30); do curl -s localhost:8088/api/books >/dev/null; done

$H upgrade --install argocd argo/argo-cd -n argocd --create-namespace --wait --timeout 10m

echo "
Next, in separate terminals (for screenshots / video):
  kubectl --context $CTX port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090   # http://localhost:9090/targets
  kubectl --context $CTX port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80   # admin/admin, dashboard 'Reading List API'
  kubectl --context $CTX port-forward -n argocd svc/argocd-server 8443:443                        # user admin
  kubectl --context $CTX -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
ArgoCD Application needs the repo pushed to GitHub (edit argocd/application.yaml repoURL), then: kubectl --context $CTX apply -f argocd/application.yaml
Cleanup: kind delete cluster --name readinglist
"
