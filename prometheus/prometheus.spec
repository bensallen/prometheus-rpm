%define debug_package %{nil}
%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

Name:		 prometheus
Version: 1.4.1
Release: 1%{?dist}
Summary: The Prometheus monitoring system and time series database.
License: ASL 2.0
URL:     https://prometheus.io

Source0: https://github.com/prometheus/prometheus/releases/download/v%{version}/prometheus-%{version}.linux-amd64.tar.gz
Source1: prometheus.service
Source2: prometheus.sysconfig

%{?systemd_requires}
%if %is_suse
Requires(pre): shadow
%else
Requires(pre): shadow-utils
%endif

%description

Prometheus is a systems and service monitoring system. It collects metrics from
configured targets at given intervals, evaluates rule expressions, displays the
results, and can trigger alerts if some condition is observed to be true.

%prep
%setup -q -n prometheus-%{version}.linux-amd64

%build
/bin/true

%install
mkdir -vp %{buildroot}/var/lib/prometheus
mkdir -vp %{buildroot}/usr/bin
mkdir -vp %{buildroot}/etc/prometheus
mkdir -vp %{buildroot}/usr/share/prometheus/console_libraries
mkdir -vp %{buildroot}/usr/share/prometheus/consoles
mkdir -vp %{buildroot}/usr/lib/systemd/system
mkdir -vp %{buildroot}/etc/sysconfig
install -m 755 prometheus %{buildroot}/usr/bin/prometheus
install -m 755 promtool %{buildroot}/usr/bin/promtool
for dir in console_libraries consoles; do
  for file in ${dir}/*; do
    install -m 644 ${file} %{buildroot}/usr/share/prometheus/${file}
  done
done
install -m 644 prometheus.yml %{buildroot}/etc/prometheus/prometheus.yml
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/prometheus.service
install -m 644 %{SOURCE2} %{buildroot}/etc/sysconfig/prometheus

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
/usr/bin/prometheus
/usr/bin/promtool
%config(noreplace) /etc/prometheus/prometheus.yml
/usr/share/prometheus
/usr/lib/systemd/system/prometheus.service
%config(noreplace) /etc/sysconfig/prometheus
%attr(755, prometheus, prometheus)/var/lib/prometheus
