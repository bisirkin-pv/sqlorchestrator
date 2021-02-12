# sqlOrchestrator

## Генерация скриптов deploy/rollback по MergeRequests Gitlab для MS SQL Server

### Сборка проекта:
```
# Контейнер с python, собирается только когда менялись зависимости
docker build --no-cache -t pythonsqlorchestration:1.1 DOCKER_ENV/

# основной образ 
docker build --no-cache -t sqlorchestrator:1.1 gitlabservice/
docker build --no-cache -t websqlorchestrator:1.1 web/

# Запуск

docker run -d --rm --name sqlorc -p 3001:3001  sqlorchestrator:1.1
docker run -d --rm --name websqlorc -p 8088:8088 websqlorchestrator:1.1

# Проверяем
docker ps

# Запускаем в браузере http://localhost:8088

# Останавливаем и удаляем 
docker rm -f sqlorc
docker rm -f websqlorc
```

## Prometheus 

### Сборка образа 
```
# Сборка и запуск
docker build -t prometheus:1.0 prometheus/
docker run -it --rm --name=prometheus prometheus:1.0

# Запуск Используя docker compose
docker-compose up -d 
```

Для сбора информации в конфиг `prometheus.yml` добвляет job
````
scrape_configs:
    - job_name: 'gitlabservice'
    static_configs:
    - targets: ['localhost:3001']
````

Смотрим [link](localhost:9090/graph)


## Работа с кластером k8s
````
# Включение ingress
sudo minikube addons enable ingress
sudo minikube addons enable ingress-dns
# запускается пару минтут, проверка статуса 
kubectl get pods -n kube-system

# deploy 
kubectl create -f sqlorc-deploy.yaml
kubectl create -f sqlorc-web-deploy.yaml

# проверка
kubectl get deployments
kubectl get rs
kubectl get pods --show-labels

# deploy service, изменение настроек через apply
kubectl create -f sqlorc-service.yaml
kubectl create -f sqlorc-web-service.yaml

kubectl get service

# Делаем доступным из вне
kubectl apply -f sqlorc-ingress.yaml 


# для того чтобы ходить по урлу а не ip, доавляется строка в /etc/hosts

# Удаление 
kubectl delete service sqlorc-server-service
kubectl delete deployment sqlorc-server

````
