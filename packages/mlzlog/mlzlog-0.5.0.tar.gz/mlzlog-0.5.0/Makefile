.PHONY: all release release-patch release-minor

all:

release-patch:
	MODE="patch" $(MAKE) release

release-minor:
	MODE="minor" $(MAKE) release

release:
	ssh jenkins.admin.frm2 -p 29417 build -v -s -p GERRIT_PROJECT=$(shell git config --get remote.origin.url | rev | cut -d '/' -f -3 | rev) -p ARCH=any -p MODE=$(MODE) ReleasePipeline
