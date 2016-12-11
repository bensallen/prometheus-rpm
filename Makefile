PACKAGES = prometheus \
alertmanager \
node_exporter \
mysqld_exporter \
blackbox_exporter

SOURCE = $(shell rpmspec -P $@/$@.spec | grep Source0 | cut -f 2 -d' ')

.PHONY: $(PACKAGES)

all: $(PACKAGES)

$(PACKAGES):

	cd $@; curl -L -O $(SOURCE)
	rpmbuild -D '_sourcedir ${PWD}/$@' -D '_topdir ${PWD}/_dist' -ba $@/$@.spec

download:
	

sign:
	docker run --rm \
		-v ${PWD}/_dist:/rpmbuild/RPMS/x86_64 \
		-v ${PWD}/bin:/rpmbuild/bin \
		-v ${PWD}/RPM-GPG-KEY-prometheus-rpm:/rpmbuild/RPM-GPG-KEY-prometheus-rpm \
		-v ${PWD}/secret.asc:/rpmbuild/secret.asc \
		-v ${PWD}/.passphrase:/rpmbuild/.passphrase \
		lest/centos7-rpm-builder \
		bin/sign

clean:
	rm -rf _dist
	rm **/*.tar.gz
