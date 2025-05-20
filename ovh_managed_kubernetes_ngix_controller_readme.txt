# Helm must be installed in your computer or laptop
# To Check if helm is installed:

helm version

# If helm is installed then continue with the next steps, else google how to install helm in your system

# You need to be connected to the OVH kubernetes cluster via ~/.kube/config

helm repo add bitnami https://charts.bitnami.com/bitnami

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm -n ingress-nginx install ingress-nginx ingress-nginx/ingress-nginx --create-namespace

# Check if ngix controller was installed correctly

kubectl get svc -n ingress-nginx ingress-nginx-controller

# With theese steps you must have a load balancer on OVH panel

