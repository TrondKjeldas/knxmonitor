
doc:
	@echo "TO RUN:"
	@echo "python -m knxmonitor knxmonitor_decoder ...."

build:
	python setup.py build bdist
	python setup.py build sdist

install:
	python setup.py install --user

# Virtualenv helpers
.PHONY: venv activate deactivate venv-clean
venv:
	@if [ -d .venv ]; then \
		echo ".venv already exists"; \
	else \
		if command -v /bin/python2 >/dev/null 2>&1; then \
			/bin/python2 -m virtualenv .venv || /bin/python2 -m ensurepip --upgrade && /bin/python2 -m virtualenv .venv; \
		else \
			python3 -m venv .venv; \
		fi; \
		echo "Created .venv"; \
	fi
	@echo "Installing test dependencies into .venv..."
	@.venv/bin/python -m ensurepip --upgrade >/dev/null 2>&1 || true
	@.venv/bin/python -m pip install --upgrade pip setuptools wheel
	@.venv/bin/python -m pip install -e '.[test]' || true
	@.venv/bin/python -m pip install --no-cache-dir mock funcsigs coverage ujson || true

activate:
	@echo "To activate the venv run:"
	@echo "  source .venv/bin/activate"

deactivate:
	@echo "To deactivate the venv run:"
	@echo "  deactivate"

venv-clean:
	@rm -rf .venv
	@echo "Removed .venv"

.PHONY: test
test:
	coverage run -m unittest discover -s test/
	coverage report -m

clean:
	rm -Rf dist build
	rm -Rf knxmonitor.egg-info
