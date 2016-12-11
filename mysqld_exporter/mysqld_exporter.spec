%define debug_package %{nil}
%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

Name:    mysqld_exporter
Version: 0.9.0
Release: 2%{?dist}
Summary: Prometheus exporter for MySQL server metrics.
License: ASL 2.0
URL:     https://github.com/prometheus/mysqld_exporter

Source0: https://github.com/prometheus/mysqld_exporter/releases/download/v%{version}/mysqld_exporter-%{version}.linux-amd64.tar.gz
Source1: mysqld_exporter.service
Source2: mysqld_exporter.sysconfig

%{?systemd_requires}
%if %is_suse
Requires(pre): shadow
%else
Requires(pre): shadow-utils
%endif

%description

Prometheus exporter for MySQL server metrics.

%prep
%setup -q -n mysqld_exporter-%{version}.linux-amd64

%build
/bin/true

%install
mkdir -vp %{buildroot}/var/lib/prometheus
mkdir -vp %{buildroot}/usr/bin
mkdir -vp %{buildroot}/usr/lib/systemd/system
mkdir -vp %{buildroot}/etc/sysconfig
install -m 755 mysqld_exporter %{buildroot}/usr/bin/mysqld_exporter
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/mysqld_exporter.service
install -m 644 %{SOURCE2} %{buildroot}/etc/sysconfig/mysqld_exporter

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
/usr/bin/mysqld_exporter
/usr/lib/systemd/system/mysqld_exporter.service
%config(noreplace) /etc/sysconfig/mysqld_exporter
%attr(755, prometheus, prometheus)/var/lib/prometheus
