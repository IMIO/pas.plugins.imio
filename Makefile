#!/usr/bin/make
.PHONY: buildout cleanall test instance


buildout.cfg:
	ln -s plone6.0.x.cfg buildout.cfg

bin/pip:
	python3 -m venv .
	touch $@

bin/buildout: bin/pip buildout.cfg
	./bin/pip install -r requirements.txt
	touch $@

buildout: bin/buildout
	./bin/buildout -t 7

test: buildout
	./bin/test

instance: buildout
	./bin/instance fg

cleanall:
	rm -rf bin develop-eggs downloads include lib parts .installed.cfg .mr.developer.cfg buildout.cfg .coverage htmlcov local pip-selfcheck.json lib64 share
