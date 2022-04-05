Name:           slow-startup
Version:        0.1
Release:        1%{?dist}
Summary:        Systemd service that takes a long time to start up

License:        MIT
Source0:        slow-startup.service

%description
Systemd service that takes a long time to start up. This is
useful for demonstrating slow startup.

%prep

%build

%install

mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE0} %{buildroot}%{_unitdir}/

%post
systemctl --no-reload enable slow-startup.service

%files
%{_unitdir}/slow-startup.service

%changelog
* Tue Apr 05 2022 Alexander Larsson <alexl@redhat.com>
- Initial version
