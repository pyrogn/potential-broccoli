init:
	python -m pip install poetry==1.8.2
	poetry install --no-root

ci-test:
	poetry run pytest -sv homework/tests

test:
	act -j build

format:
	poetry run ruff format .

lint:
	poetry run ruff check .