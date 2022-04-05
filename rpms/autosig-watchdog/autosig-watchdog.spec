Name:           autosig-watchdog
Version:        0.1
Release:        1%{?dist}
Summary:        Tools for handling the autosig runvm external watchdog

License:        MIT
Source0:        watchdog-start
Source1:        watchdog-stop
Source2:        watchdog-ostree-start.service
Source3:        watchdog-ostree-stop.service

%description
Tools for handling the autosig runvm external watchdog

%prep

%build

%install

mkdir -p %{buildroot}%{_bindir}
install  -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/
install  -m 0755 %{SOURCE1} %{buildroot}%{_bindir}/

mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/
install -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/

%files
%{_bindir}/watchdog-start
%{_bindir}/watchdog-stop
%{_unitdir}/watchdog-ostree-start.service
%{_unitdir}/watchdog-ostree-stop.service

%changelog
* Tue Apr 05 2022 Alexander Larsson <alexl@redhat.com>
- Initial version
