# Makefile for Phelomia development and deployment

.PHONY: help install dev test lint format build run clean docker-build docker-run deploy

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Default target
help: ## Show this help message
	@echo "Phelomia Development Commands"
	@echo "============================="
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
install: ## Install dependencies
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

setup: ## Run initial setup
	@echo "Running setup script..."
	chmod +x setup.sh
	./setup.sh

dev: ## Start development server
	@echo "Starting development server..."
	$(PYTHON) src/app.py --reload

test: ## Run tests
	@echo "Running tests..."
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing

test-fast: ## Run fast tests only
	@echo "Running fast tests..."
	$(PYTEST) tests/ -v -m "not slow"

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	$(PYTEST) tests/ -v -m "integration"

##@ Code Quality
lint: ## Run linting
	@echo "Running linting..."
	$(FLAKE8) src/ tests/
	$(BLACK) --check src/ tests/

format: ## Format code
	@echo "Formatting code..."
	$(BLACK) src/ tests/
	isort src/ tests/

type-check: ## Run type checking
	@echo "Running type checking..."
	mypy src/

security-check: ## Run security checks
	@echo "Running security checks..."
	bandit -r src/
	safety check

quality: lint type-check security-check ## Run all quality checks

##@ Building
build: ## Build the application
	@echo "Building application..."
	$(PYTHON) setup.py build

build-wheel: ## Build wheel package
	@echo "Building wheel package..."
	$(PYTHON) setup.py bdist_wheel

##@ Docker
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	$(DOCKER) build -t phelomia:latest .

docker-build-gpu: ## Build GPU Docker image
	@echo "Building GPU Docker image..."
	$(DOCKER) build -f Dockerfile.gpu -t phelomia:gpu .

docker-run: ## Run Docker container
	@echo "Running Docker container..."
	$(DOCKER) run -p 7860:7860 -v $(PWD)/logs:/app/logs -v $(PWD)/data:/app/data phelomia:latest

docker-dev: ## Run Docker container in development mode
	@echo "Running Docker container in development mode..."
	$(DOCKER) run -p 7860:7860 -v $(PWD):/app -e PHELOMIA_DEBUG=true phelomia:latest

##@ Docker Compose
up: ## Start all services with docker-compose
	@echo "Starting all services..."
	$(DOCKER_COMPOSE) up -d

up-gpu: ## Start GPU services
	@echo "Starting GPU services..."
	$(DOCKER_COMPOSE) --profile gpu up -d

up-prod: ## Start production services
	@echo "Starting production services..."
	$(DOCKER_COMPOSE) --profile production up -d

up-monitoring: ## Start with monitoring
	@echo "Starting services with monitoring..."
	$(DOCKER_COMPOSE) --profile monitoring up -d

down: ## Stop all services
	@echo "Stopping all services..."
	$(DOCKER_COMPOSE) down

logs: ## Show logs
	@echo "Showing logs..."
	$(DOCKER_COMPOSE) logs -f

##@ Deployment
deploy-staging: ## Deploy to staging
	@echo "Deploying to staging..."
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.staging.yml up -d

deploy-prod: ## Deploy to production
	@echo "Deploying to production..."
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

backup: ## Create backup
	@echo "Creating backup..."
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/ logs/ results/

restore: ## Restore from backup
	@echo "Restoring from backup..."
	@read -p "Enter backup file name: " backup_file; \
	tar -xzf $$backup_file

##@ Monitoring
health-check: ## Check application health
	@echo "Checking application health..."
	curl -f http://localhost:7860/health || echo "Health check failed"

metrics: ## Show metrics
	@echo "Application metrics:"
	curl -s http://localhost:7860/metrics | head -20

##@ Database
migrate: ## Run database migrations
	@echo "Running migrations..."
	# Add migration commands here

seed: ## Seed database with sample data
	@echo "Seeding database..."
	$(PYTHON) scripts/seed_data.py

##@ Maintenance
clean: ## Clean up temporary files
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

clean-docker: ## Clean Docker images and containers
	@echo "Cleaning Docker resources..."
	$(DOCKER) system prune -af
	$(DOCKER) volume prune -f

clean-logs: ## Clean log files
	@echo "Cleaning logs..."
	find logs/ -name "*.log" -mtime +30 -delete

##@ Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	sphinx-build -b html docs/ docs/_build/

docs-serve: ## Serve documentation locally
	@echo "Serving documentation..."
	cd docs/_build && $(PYTHON) -m http.server 8080

##@ Release
version: ## Show current version
	@echo "Current version:"
	@$(PYTHON) -c "import src; print(src.__version__)" 2>/dev/null || echo "Version not found"

tag: ## Create git tag
	@read -p "Enter version tag (e.g., v1.0.0): " tag; \
	git tag -a $$tag -m "Release $$tag"; \
	git push origin $$tag

release: test quality build ## Prepare release
	@echo "Release prepared successfully!"

##@ CI/CD
ci-test: ## Run CI tests
	@echo "Running CI tests..."
	$(PYTEST) tests/ --junitxml=test-results.xml --cov=src --cov-report=xml

ci-build: ## Build for CI
	@echo "Building for CI..."
	$(DOCKER) build -t phelomia:ci .

##@ Local Development
notebook: ## Start Jupyter notebook
	@echo "Starting Jupyter notebook..."
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

shell: ## Start Python shell with app context
	@echo "Starting Python shell..."
	$(PYTHON) -c "from src.app import *; print('Phelomia shell ready!')"

db-shell: ## Start database shell
	@echo "Starting database shell..."
	# Add database shell command here

##@ Utilities
requirements: ## Update requirements.txt
	@echo "Updating requirements.txt..."
	pip-compile requirements.in

requirements-dev: ## Update requirements-dev.txt
	@echo "Updating requirements-dev.txt..."
	pip-compile requirements-dev.in

check-deps: ## Check for outdated dependencies
	@echo "Checking dependencies..."
	$(PIP) list --outdated

update-deps: ## Update dependencies
	@echo "Updating dependencies..."
	$(PIP) install --upgrade -r requirements.txt

pre-commit: ## Run pre-commit hooks
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

# Performance testing
benchmark: ## Run performance benchmarks
	@echo "Running benchmarks..."
	$(PYTEST) tests/ -m "performance" --benchmark-only

# Load testing
load-test: ## Run load tests
	@echo "Running load tests..."
	# Add load testing command here

##@ Environment
env-check: ## Check environment setup
	@echo "Environment Check"
	@echo "=================="
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Docker: $(shell $(DOCKER) --version)"
	@echo "Docker Compose: $(shell $(DOCKER_COMPOSE) --version)"
	@echo "Git: $(shell git --version)"

env-info: ## Show environment information
	@echo "Environment Information"
	@echo "======================="
	@echo "Current directory: $(PWD)"
	@echo "Python executable: $(shell which $(PYTHON))"
	@echo "Virtual environment: $(VIRTUAL_ENV)"
	@echo "Platform: $(shell uname -a)"