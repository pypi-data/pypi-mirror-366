# Find more information at ase.vu.nl/docs/framework/glossary/makefiles

# Since we are using uv to manage our dependencies, we can utilize the "uv run python ..."
# command which makes sure to launch the python script with the dependencies installed as
# defined by the pyproject.toml file. That makes it the single source of truth and we 
# can generate a requirements.txt file from there.



# We always want to run lint checks before we build or test
lint:
	@echo "Linting src and tests"
	@uv run ruff check src tests

# This will generate a python package that can be published and installs it locally for
# testing. Note, that it installs it with the -e (editable) option which means that when
# changing any library files, you can immediately test them and don't have to re-install
# with 'uv build'. However if we want to publish, we must always build.
build: lint
	@rm -rf dist/
	@uv build
	@uv pip compile pyproject.toml -o requirements.txt

# Add all test files into /tests they will all get run when this target is invoked
test: lint
	@uv run pytest

# Open a python repl for quick debugging
repl:
	uv run python


clean:
	uv cache clean
	rm -r .pytest_cache .ruff_cache .venv dist



# Set token: export UV_PUBLISH_TOKEN=(token)
# check token: echo $UV_PUBLISH_TOKEN

check-publish-token:
	@if [ -z "$(UV_PUBLISH_TOKEN)" ]; then \
		echo "Error: UV_PUBLISH_TOKEN environment variable is not set"; \
		exit 1; \
	else \
		echo "UV_PUBLISH_TOKEN is set"; \
	fi



publish-test: check-publish-token build
	@echo "Publishing to test.pypi.org"
	@uv publish dist/* --index testpypi


publish: check-publish-token build
	@echo "Publishing to pypi.org"
	@uv publish dist/* --index pypi


# Install with python3 -m pip install --index-url https://test.pypi.org/simple/ roverlib

