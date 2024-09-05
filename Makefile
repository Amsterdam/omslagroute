.PHONY: manifests deploy

dc = docker compose

ENVIRONMENT ?= local
HELM_ARGS = manifests/chart \
	-f manifests/values.yaml \
	-f manifests/env/${ENVIRONMENT}.yaml \
	--set image.tag=${VERSION}

REGISTRY ?= 127.0.0.1:5001
REPOSITORY ?= salmagundi/wonen-omslagroute
VERSION ?= latest
CHART_VERSION ?= 1.9.1

all: build push deploy fixtures

build:
	$(dc) build

test:
	echo "No tests available"

migrate:
	echo "no migrations"

fixtures: migrate

push:
	$(dc) push


manifests:
	@helm template wonen-omslagroute $(HELM_ARGS) $(ARGS)

deploy: manifests
	helm upgrade --install wonen-omslagroute $(HELM_ARGS) $(ARGS)

update-chart:
	rm -rf manifests/chart
	git clone --branch $(CHART_VERSION) --depth 1 git@github.com:Amsterdam/helm-application.git manifests/chart
	rm -rf manifests/chart/.git

clean:
	$(dc) down -v --remove-orphans

reset:
	kubectl delete deployment wonen-omslagroute-wonen-omslagroute && kubectl delete ingress wonen-omslagroute-internal-wonen-omslagroute && helm uninstall wonen-omslagroute

refresh: reset build push deploy

dev:
	nohup kubycat kubycat-config.yaml > /dev/null 2>&1&
