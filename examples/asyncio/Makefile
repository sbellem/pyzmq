.PHONY: clean clean-pyc help

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef

export PRINT_HELP_PYSCRIPT



help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-pyc

clean-pyc: ## remove Python file artifacts
	docker-compose run --no-deps --rm sub find . -name '*.pyc' -exec rm -f {} +
	docker-compose run --no-deps --rm sub find . -name '*.pyo' -exec rm -f {} +
	docker-compose run --no-deps --rm sub find . -name '*~' -exec rm -f {} +
	docker-compose run --no-deps --rm sub find . -name '__pycache__' -exec rm -fr {} +

down: ## stop and remove containers, networks, images, and volumes
	docker-compose down

stop:
	docker-compose stop pubrouter sub dealer

rm:
	docker-compose rm --stop --force pubrouter sub dealer

run: rm ## run the example
	docker-compose up -d
	sh follow-logs-with-tmux.sh

run-without-tmux: rm ## run the example
	docker-compose up
