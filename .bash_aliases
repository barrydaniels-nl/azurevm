alias k=kubectl
alias kp="kubectl run temp-shell-pod  --rm -it --image bretfisher/netshoot -- bash"
alias ktx="kubectx"
alias kns="kubens"
alias ktl="kubetail"
alias azl="az login --use-device-code"
alias azs="az account set --subscription 4a7aa471-58a1-4b1c-88e9-c9025ca5ee57"
alias aksl="az aks get-credentials --resource-group dev-bbn1-rg --name dev-bbn1-blue-aks"
alias azh="cat ~/.bash_aliases"
alias podlist="kubectl get pods -n dso-api -o json | jq '.items[] | .metadata.name'"
alias pods="kubectl get pods -n dso-api -o wide"
alias dsologs='kubectl logs -l app=dso-api -n dso-api --max-log-requests 50 -f'
alias reload='kubectl rollout restart deployment dso-api -n dso-api'
