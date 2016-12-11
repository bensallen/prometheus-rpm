%define debug_package %{nil}

Name:    node_exporter
Version: 0.13.0
Release: 1%{?dist}
Summary: Prometheus exporter for machine metrics, written in Go with pluggable metric collectors.
License: ASL 2.0
URL:     https://github.com/prometheus/node_exporter

Source0: https://github.com/prometheus/node_exporter/releases/download/v%{version}/node_exporter-%{version}.linux-amd64.tar.gz
Source1: node_exporter.service
Source2: node_exporter.sysconfig

%{?systemd_requires}
Requires(pre): shadow-utils

%description

Prometheus exporter for machine metrics, written in Go with pluggable metric collectors.

%prep
%setup -q -n node_exporter-%{version}.linux-amd64

%build
/bin/true

%install
mkdir -vp %{buildroot}/var/lib/prometheus
mkdir -vp %{buildroot}/usr/bin
mkdir -vp %{buildroot}/usr/lib/systemd/system
mkdir -vp %{buildroot}/etc/sysconfig
install -m 755 node_exporter %{buildroot}/usr/bin/node_exporter
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/node_exporter.service
install -m 644 %{SOURCE2} %{buildroot}/etc/sysconfig/node_exporter

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d /var/lib/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0

%post
if [ $1 -eq 1 ] ; then
        # Initial installation
        systemctl preset %{name}.service >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
        systemctl stop %{name}.service > /dev/null 2>&1 || :
fi

%postun
systemctl daemon-reload >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
/usr/bin/node_exporter
/usr/lib/systemd/system/node_exporter.service
%config(noreplace) /etc/sysconfig/node_exporter
%attr(755, prometheus, prometheus)/var/lib/prometheus
