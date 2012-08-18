# Pomidorka - time management toolkit supporting pomidoro technique
# Makefile
# Copyright (C) 2010-2011 Ilya Paramonov

prefix=/usr/local

all: build-translations

help:
	@echo 'Targets:'
	@echo '  update-translations - update all .ts-files'
	@echo '  build-translations  - build all .ts-files'
	@echo '  documentation       - create documentation using epydoc'
	@echo '  clean               - remove files created by other targets'
	@echo '  clean-binaries	     - remove python binaries'
	@echo '  pylint              - run pylint static checker for all code'
	@echo '  pylint-hook         - run pylint static checker from mercurial hook'
	@echo '  unittest            - run all unit tests (can be used as a hook)'

update-translations:
	pyside-lupdate `find . -name '*.py'` -ts `find translations -name '*.ts'` -noobsolete

build-translations: $(patsubst %.ts,%.qm,$(wildcard translations/*.ts))

%.qm: %.ts
	lrelease $<

documentation:
	find src -name '*.py' -a ! -wholename 'test/*' | \
		xargs epydoc -v --name 'Smart Conference ECG Monitoring' --graph all $(EPYPARAMS)

clean: clean-binaries
	rm -f $(patsubst %.ts,%.qm,$(wildcard translations/*.ts))
	rm -rf html

clean-binaries:
	find . -name '*.py[co]' | xargs -r rm

pylint:
	find pomidorka -name '*.py' -a -not -regex '^test.*' | \
	PYTHONPATH='pomidorka' xargs pylint --rcfile=pylint.conf

pylint-hook:
	hg status -am --change ${HG_NODE} -I 'glob:**.py' | cut -d ' ' -f 2 | \
	PYTHONPATH='pomidorka' xargs -r pylint --rcfile=pylint.conf

unittest:
	UNITTEST=1 PYTHONPATH='pomidorka' nosetests3 test/

.PHONY: help all update-translations build-translations version documentation clean pylint pylint-hook unittest
