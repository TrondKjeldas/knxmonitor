
doc:
	@echo "TO RUN:"
	@echo "python -m knxmonitor knxmonitor_decoder ...."
	
build:
	python setup.py build bdist
	python setup.py build sdist

install:
	python setup.py install --user

.PHONY: test
test:
	coverage run -m unittest discover -s test/

clean:
	rm -Rf dist build
	rm -Rf knxmonitor.egg-info
