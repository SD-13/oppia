.DEFAULT_GOAL := oneshot
HELP_SPACING ?= 30
PACKAGE_NAME := dev-tools
SOURCE_TAG ?= $(TAG)

CONTAINERS := redis devserver firebase elasticsearch cloud-datastore frontend

SHELL_PREFIX=docker-compose exec -e
WAIT_FOR_PORT=timeout 60 bash -c 'until printf "" 2>>/dev/null >>/dev/tcp/localhost/8181; do sleep 1; done'

build:  # Build the docker images
	docker-compose build --no-cache

up:
	docker-compose up -d

$(CONTAINERS):
	docker-compose up -d $@

logs:
	docker-compose logs -f --tail=300

stop:
	docker-compose stop

shell:
	${SHELL_PREFIX} devserver /bin/bash

destroy:
	docker-compose down

oneshot: devserver frontend
	@echo "\033[0;33mWaiting for server to start..."
	@${WAIT_FOR_PORT}
	@echo "\033[0;32mVisit Oppia at http://localhost:8181"
