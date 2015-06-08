.PHONY: test
test: install
	py.test

.PHONY: install
install: requirements
	python setup.py install
	make clean

.PHONY: requirements
requirements:
	pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf build dist slackrtm.egg-info
