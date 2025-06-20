Name:           rebase--
Version:        0.01
Release:        1%{?dist}
Summary:        back-to-basics rebasing tool.

License:        GPLv2
URL:            https://github.com/eantoranz/rebase--
Source0:        https://github.com/eantoranz/rebase--

Requires:       python3.11
Requires:       python3-pygit2

%description
back-to-basics rebasing tool.

%prep
%autosetup


#%build
#%make_build


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/python3.9/site-packages/
install -m 555 rebase-- %{buildroot}%{_bindir}
install -m 444 rebasedashdash.py %{buildroot}%{_libdir}/python3.9/site-packages/

%files
%{_bindir}/*
%{_libdir}/*


%changelog
* Sun Jun 15 2025 Edmundo Carmona Antoranz
- Initial release using v0.01
