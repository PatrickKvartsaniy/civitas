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

.PHONY: deploy
deploy:
	terraform -chdir=deploy fmt
	terraform -chdir=deploy init
	terraform -chdir=deploy plan
	terraform -chdir=deploy apply -auto-approve -var-file=tfvars/main.tfvars

.PHONY: kill
kill:
    terraform -chdir=deploy destroy -auto-approve

.PHONY: destroy
destroy:
	terraform -chdir=deploy destroy -auto-approve
