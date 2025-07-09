.PHONY: install test lint format clean build docker

install:
	pip install -e .[dev]

test:
	pytest tests/ -v

lint:
	black --check .
	isort --check-only .
	flake8 src/

format:
	black .
	isort .

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:
	python -m build

docker:
	docker build -t sqlmagic .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down