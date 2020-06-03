#!/usr/bin/make
.PHONY: buildout cleanall test instance


buildout.cfg:
	ln -s plone4.3.x.cfg buildout.cfg

bin/pip:
	if [ -f /usr/bin/virtualenv-2.7 ] ; then virtualenv-2.7 .;else virtualenv -p python2.7 .;fi
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

devpy3:
	virtualenv -p python3 .
	ln -s plone5.2.x.cfg buildout.cfg
	./bin/pip install -r requirements.txt
	./bin/buildout -Nt 7
