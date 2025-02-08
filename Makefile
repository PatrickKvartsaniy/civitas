.PHONY: run_web
run_web:
	poetry run python main.py web

.PHONY: run_etl
run_etl:
	poetry run python main.py etl

.PHONY: deps
deps:
	poetry check
	poetry update
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	cp requirements.txt deploy/requirements.txt

.PHONY: tf-init
tf-init:
	terraform -chdir=deploy init

.PHONY: tf-plan
tf-plan:
	terraform -chdir=deploy plan

.PHONY: deploy
deploy:
	terraform -chdir=deploy apply -auto-approve

.PHONY: tf-destroy
tf-destroy:
	terraform -chdir=deploy destroy -auto-approve
