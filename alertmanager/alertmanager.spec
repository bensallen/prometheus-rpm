%define debug_package %{nil}
%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

Name:		 alertmanager
Version: 0.5.1
Release: 1%{?dist}
Summary: Prometheus Alertmanager.
License: ASL 2.0
URL:     https://github.com/prometheus/alertmanager

Source0: https://github.com/prometheus/alertmanager/releases/download/v%{version}/alertmanager-%{version}.linux-amd64.tar.gz
Source1: alertmanager.service
Source2: alertmanager.sysconfig

%{?systemd_requires}
%if %is_suse
Requires(pre): shadow
%else
Requires(pre): shadow-utils
%endif

%description

The Alertmanager handles alerts sent by client applications such as the
Prometheus server. It takes care of deduplicating, grouping, and routing them to
the correct receiver integration such as email, PagerDuty, or OpsGenie. It also
takes care of silencing and inhibition of alerts.

%prep
%setup -q -n alertmanager-%{version}.linux-amd64

%build
/bin/true

%install
mkdir -vp %{buildroot}/var/lib/prometheus
mkdir -vp %{buildroot}/usr/bin
mkdir -vp %{buildroot}/etc/prometheus
mkdir -vp %{buildroot}/usr/lib/systemd/system
mkdir -vp %{buildroot}/etc/sysconfig
install -m 755 alertmanager %{buildroot}/usr/bin/alertmanager
install -m 644 simple.yml %{buildroot}/etc/prometheus/alertmanager.yml
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/alertmanager.service
install -m 644 %{SOURCE2} %{buildroot}/etc/sysconfig/alertmanager

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
/usr/bin/alertmanager
%config(noreplace) /etc/prometheus/alertmanager.yml
/usr/lib/systemd/system/alertmanager.service
%config(noreplace) /etc/sysconfig/alertmanager
%attr(755, prometheus, prometheus)/var/lib/prometheus
