#
# Copyright (c) 2022, Panagiotis Tsirigotis

# This file is part of linuxnet-iptables.
#
# linuxnet-iptables is free software: you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public
# License as published by the Free Software Foundation.
#
# linuxnet-iptables is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with linuxnet-iptables. If not, see
# <https://www.gnu.org/licenses/>.
#

PACKAGE			= linuxnet-iptables

PYTHON                  = python3

default: description

description:
	@echo
	@echo "Targets:"
	@echo
	@echo "   build       : build the package"
	@echo "   install     : install the package"
	@echo "   man         : make manpages"
	@echo "   html        : make html documentation"
	@echo "   sdist       : make source distribution"
	@echo "   test        : run unit tests"
	@echo "   lint        : run pylint against the linuxnet.iptables modules;"
	@echo "                 send all output to PAGER"
	@echo "   clean       : remove all build products"
	@echo


#
# This is a list of targets that will be tested via 'make _target_test'
# These are the publically available makefile targets except for the
# 'install' target which is excluded because installation privileges
# may not be available.
# If making a target fails, the file make.<target> will contain the
# output (and standard error) of the failed make command.
#
_TARGETS = build man html sdist test lint

_target_test:
	@true ;\
	for target in $(_TARGETS) ; do \
	    output=make.$$target ;\
	    echo -n "Target: $$target ....    " ;\
	    if $(MAKE) $$target > $$output 2>&1 ; then \
		echo "OK" ;\
		rm $$output ;\
	    else \
		echo "FAILED" ;\
		echo "Check file $$output for details" ;\
		exit 1;\
	    fi ;\
	    output=make.clean ;\
	    if $(MAKE) clean > $$output 2>&1 ; then \
		rm $$output ;\
	    else \
		echo "Clean target failed: check file $$output for details" ;\
	    fi ;\
	done

man: _sphinx_check
	@$(MAKE) -C docs $@

html: _sphinx_check
	@$(MAKE) -C docs $@

#
# Require Sphinx-4.4 or later.
#
# NB: probably all Sphinx 4.x versions should work, and that test
#     could be relaxed (I have only tested with Sphinx-4.4.0)
#
_sphinx_check:
	@true ;\
	sphinxbuild=`command -v sphinx-build` ;\
	if test -z "$$sphinxbuild" ; then \
	    echo "Sphinx not available" ;\
	    exit 1 ;\
	fi ;\
	version=`sphinx-build --version | awk '{print $$2}'` ;\
	major_version=`echo $$version | cut -d. -f1` ;\
	if test $$major_version -lt 4 ; then \
	    echo "Sphinx version 4.4 or later is required (existing=$$version)" ;\
	    exit 1 ;\
	fi ;\
	if test $$major_version -eq 4 ; then \
	    minor_version=`echo $$version | cut -d. -f2` ;\
	    if test $$major_version -eq 4 -a $$minor_version -lt 4 ; then \
		echo "Sphinx version 4.4 or later is required (existing=$$version)" ;\
		exit 1 ;\
	    fi ;\
	fi

sdist: MANIFEST.in
	@true ;\
	$(PYTHON) setup.py sdist ;\
	tarball=`find dist -name '*.tar.gz' -print` ;\
	if test -n "$$tarball" ; then \
	    echo "CREATED: $$tarball" ;\
	else \
	    echo "FAILED to create source distribution" ;\
	    exit 1 ;\
	fi

build:
	LC_ALL=en_US.utf-8 $(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install

test:
	$(PYTHON) setup.py test

#
# Check for pylint 2.11.x (the one I currently use)
#
_lint_check:
	@true ;\
	pylint=`command -v pylint` ;\
	if test -z "$$pylint" ; then \
	    echo "pylint not available" ;\
	    exit 1 ;\
	fi ;\
	version=`pylint --version | grep pylint | awk '{print $$2}'` ;\
	major_version=`echo $$version | cut -d. -f1` ;\
        minor_version=`echo $$version | cut -d. -f2` ;\
	if test $$major_version -eq 2 -a $$minor_version -eq 11 ; then \
            true ;\
        else \
	    echo "Only version 2.11.x is supported (existing=$$version)" ;\
	    exit 1 ;\
	fi

lint: _lint_check
	@true ;\
        source_dir=`echo $(PACKAGE) | tr - /` ;\
	pyfiles=`find $$source_dir -name '*.py' -print` ;\
	echo "Linting iptables files:" ;\
	for pyfile in $$pyfiles ; do \
	    echo "    $$pyfile" ;\
	done ;\
	if test -n "$(PAGER)" ; then \
	    pylint --rcfile .pylintrc $$pyfiles 2>&1 | $(PAGER) ;\
	else \
	    pylint --rcfile .pylintrc $$pyfiles ;\
	fi

clean: _clean_pycache _clean_log _clean_docs _clean_dirs

_clean_pycache:
	@true ;\
	dirlist=`find . -name __pycache__ -type d -print` ;\
	if test -n "$dirlist" ; then \
	    for dir in $$dirlist ; do \
		rm -rf $$dir ;\
		echo "Deleted: $$dir" ;\
	    done \
	fi

_clean_log:
	@find . -name test.log -type f -print | xargs rm -f

_clean_docs:
	@true ;\
	sphinxbuild=`command -v sphinx-build` ;\
	if test -n "$$sphinxbuild" ; then \
	    $(MAKE) -C docs clean ;\
	fi

_clean_dirs:
	@true ;\
        egg_info=`echo $(PACKAGE) | tr - _`.egg-info ;\
	for f in build dist $$egg_info ; do \
            if test -d $$f ; then \
                rm -r $$f || exit 1 ;\
                echo "Deleted: $$f" ;\
            fi \
        done
