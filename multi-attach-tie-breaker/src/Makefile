.PHONY: setup test run docker-build-push

setup:
	@echo "Setting up the environment..."
	@pip install -r requirements.txt >> /dev/null

test: setup
	@echo "Running tests..."
	@python -m pytest . -s  -vv

run: setup
	@echo "Running the application..."
	@python multi_attach_tie_breaker.py

docker-build-push:
	docker buildx build --platform linux/amd64,linux/arm64 -t rudderstack/multi_attach_tie_breaker:v1.0.0 . --push