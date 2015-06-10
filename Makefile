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

.PHONY: publish
publish:
	pandoc -s -w rst README.md -o README.rs
	python setup.py sdist upload
	rm README.rs
