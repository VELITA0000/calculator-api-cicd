# Practica 4 - Calculadora API CI/CD con Kubernetes (EKS)

Implementacion de una API REST de calculadora con pipeline CI/CD en GitHub Actions:

- `integrate`: corre tests en Pull Requests a `main`.
- `delivery`: construye y publica imagen en Docker Hub al crear tag `v*`.
- `deploy`: despliega en Kubernetes cuando `delivery` termina con exito.


## Despliegue del proyecto

### Preparar terminal

Abre terminal de PowerShell en VSCode y ejecuta:

```powershell
Set-Location "D:\VSCODE\ITESO\DESARROLLO EN LA NUBE\PRACTICA"
```

### Herramientas

```powershell
git --version
python --version
docker --version
aws --version
kubectl version --client
eksctl version
```

### Instalar faltantes con winget

```powershell
winget --version
```

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id Docker.DockerDesktop -e

winget install --id Amazon.AWSCLI -e
winget install --id Kubernetes.kubectl -e
winget install --id Weaveworks.eksctl -e
```

### Estructura del proyecto

Ya debes tener en `Practica_4`:

- `app/main.py`
- `tests/test_main.py`
- `requirements.txt`
- `Dockerfile`
- `.github/workflows/integrate.yml`
- `.github/workflows/delivery.yml`
- `.github/workflows/deploy.yml`
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `README.md`, `GUIA.md`, `EXECUTE.md`

### Crear y activar entorno virtual

**Crear venv**   
```powershell
cd <proyecto>
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python --version
pip --version
```

**Reactivar venv**   
```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar dependencias

**Instalar dependencias**    
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Probar API local

**Ver pruebas:**     
```powershell
$env:PYTHONPATH = (Get-Location).Path
pytest tests\
```

**Terminal 1:**     
```powershell
Set-Location "D:\VSCODE\ITESO\DESARROLLO EN LA NUBE\PRACTICA\Practica_4"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2:**      
```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/sum" -ContentType "application/json" -Body '{"a":20,"b":5}'
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/subtract" -ContentType "application/json" -Body '{"a":20,"b":5}'
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/multiply" -ContentType "application/json" -Body '{"a":20,"b":5}'
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/divide" -ContentType "application/json" -Body '{"a":20,"b":5}'
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/divide" -ContentType "application/json" -Body '{"a":20,"b":0}'
```

### Inicializar Git y crear repositorio GitHub

**Crea repo nuevo:**     
`calculator-api-cicd`

**Subir api a repo:**     
```powershell
Set-Location "D:\VSCODE\ITESO\DESARROLLO EN LA NUBE\PRACTICA\Practica_4"
git init
git add .
git commit -m "feat: api calculator with ci cd and kubernetes manifests"
git branch -M main
git remote add origin <REPO URL>
git push -u origin main
```

**Verificar que se subieron**    
```powershell
git status
git remote -v
git branch -vv
```

### Branch para suma

**Actualizar suma en rama**  
```powershell
git checkout -b feat/suma
# haz ajuste menor relacionado a suma (ej. mensaje, test o validacion)
git add .
git commit -m "feat: update sum operation"
git push -u origin feat/suma
```

**Abre PR en GitHub:**   
`feat/suma -> main`.

### Branch para resta

**Actualizar resta en rama**  
```powershell
git checkout main
git pull
git checkout -b feat/resta
# haz ajuste menor relacionado a resta
git add .
git commit -m "feat: update subtract operation"
git push -u origin feat/resta
```

**Abre PR en GitHub:**   
`feat/resta -> main`.

Cada PR debe ejecutar el workflow `integrate`.

### Configurar Branch Protection en main

En GitHub:

`Settings > Branches > Add branch protection rule`

Configura:
- Branch name pattern: main
- Require a pull request before merging
- Require status checks to pass before merging
- Selecciona check `integrate`

### Configurar Docker Hub para delivery

1. Crea un Access Token en Docker Hub (profile settings - personal access tokens - create token)
2. Verifica localmente login:

```powershell
docker login -u <TU_USUARIO_DOCKERHUB>
```

Ingresar password: (token)

### Configurar AWS Lab

Tus credenciales expiran cada 4 horas. Cada inicio o expiracion:

```powershell
aws configure
AWS Access Key ID:
AWS Secret Access Key:
AWS Session Token:
region name [us-east-1]: enter
output format [json]: enter

aws sts get-caller-identity
```

### Crear cluster Kubernetes con EKS

```powershell
Set-Location "D:\VSCODE\ITESO\DESARROLLO EN LA NUBE\PRACTICA\Practica_4"
eksctl create cluster -f k8s/cluster.yaml

kubectl get nodes

eksctl delete cluster --region us-east-1 --name practica-k8s
```

### Preparar kubeconfig y secret para GitHub Actions

Ya con cluster creado:

```powershell
kubectl config current-context
$KUBECONFIG_B64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\.kube\config"))
$KUBECONFIG_B64
```

Copia salida de `base64` para el secret `KUBECONFIG_B64`.

### Configurar secrets del repo en GitHub

En `Settings > Secrets and variables > Actions`, agrega:

- `DOCKERHUB_USERNAME` = tu usuario Docker Hub
- `DOCKERHUB_TOKEN` = token Docker Hub
- `KUBECONFIG_B64` = salida base64 de tu kubeconfig
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` = mismas credenciales temporales del Lab (las mismas que usas con `aws configure`)

El workflow `deploy` ejecuta `kubectl` contra EKS; el kubeconfig llama internamente a `aws eks get-token`. En GitHub Actions no existe tu perfil local de AWS, por eso el job exporta `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` y `AWS_SESSION_TOKEN` desde secrets. Cuando el Lab caduca (cada ~4 horas), actualiza esos tres secrets y vuelve a lanzar el job `deploy` (por ejemplo con **Re-run failed jobs** en Actions).

Si ves **The request signature we calculated does not match the signature you provided**:

1. Borra y vuelve a crear los tres secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) copiando de nuevo el panel del Learner Lab en la misma sesion (las tres deben ir juntas).
2. Sin espacios al inicio o al final, sin comillas en el valor del secret, sin pegar la linea `export AWS_...=`.
3. Confirma que no intercambiaste Access Key y Secret Key entre si.
4. En local, prueba con las mismas tres variables: `aws sts get-caller-identity` debe funcionar antes de volver a pegarlas en GitHub.

### Abrir puerto NodePort 30080 en Security Group (EKS)

```powershell
$CLUSTER_SG = aws eks describe-cluster --name practica-k8s --query 'cluster.resourcesVpcConfig.clusterSecurityGroupId' --output text

aws ec2 authorize-security-group-ingress --group-id $CLUSTER_SG --protocol tcp --port 30080 --cidr 0.0.0.0/0
```

### Merge a `main` y release con tag semantico

Cuando PRs esten en verde, mergea en GitHub.

Luego en local:

```powershell
Set-Location "D:\VSCODE\ITESO\DESARROLLO EN LA NUBE\PRACTICA\Practica_4"
git checkout main
git pull
git tag v1.0.0
git push origin v1.0.0
```

Esto dispara:

1. `delivery` (build + push a Docker Hub)
2. `deploy` (kubectl apply al cluster)

### Verificar deployment en Kubernetes

```powershell
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get nodes -o wide
```

Obtiene una IP externa de nodo y prueba endpoints:

```powershell
Invoke-RestMethod -Method Get -Uri "http://<EXTERNAL-IP>:30080/health"
Invoke-RestMethod -Method Post -Uri "http://<EXTERNAL-IP>:30080/sum" -ContentType "application/json" -Body '{"a":11,"b":7}'
Invoke-RestMethod -Method Post -Uri "http://<EXTERNAL-IP>:30080/subtract" -ContentType "application/json" -Body '{"a":11,"b":7}'
```

### Limpiar

```powershell
eksctl delete cluster --region us-east-1 --name practica-k8s
```
