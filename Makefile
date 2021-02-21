.PHONY: fix
fix:
	poetry run black .
	poetry run isort .

.PHONY: lint
lint:
	poetry run mypy --strict .
	poetry run pylint calibpy
	poetry run black --check .
	poetry run isort -c -rc .

.PHONY: test
test:
	poetry run pytest \
	--cov=calibpy \
	--cov-report=xml \
	--cov-report=term-missing \
	-vv \
	-W default \
	--log-level=DEBUG \
	t
