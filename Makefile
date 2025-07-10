.PHONY: install test lint format clean build docker

install:
	poetry install --with dev

test:
	poetry install
	poetry run pytest tests/ -v

lint:
	poetry run black --check .
	poetry run isort --check-only .
	poetry run ruff check src/

format:
	poetry run black .
	poetry run isort .
	poetry run ruff check src/ --fix

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:
	poetry build

run:
	poetry run sqlmagic

docker:
	docker build -t sqlmagic .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down