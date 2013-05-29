Summary:	Cluster-based virtualization management software
Name:		ganeti
Version:	2.6.2
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	https://ganeti.googlecode.com/files/%{name}-%{version}.tar.gz
# Source0-md5:	9d9a0c5c0341d5775988961449f82b99
URL:		https://code.google.com/p/ganeti/
BuildRequires:	fakeroot
BuildRequires:	gawk
BuildRequires:	ghc
BuildRequires:	ghc-QuickCheck
BuildRequires:	ghc-curl
BuildRequires:	ghc-haskell-platform
BuildRequires:	ghc-json
BuildRequires:	hlint
BuildRequires:	hscolour
BuildRequires:	python
BuildRequires:	python-affinity
BuildRequires:	python-modules
BuildRequires:	python-paramiko
BuildRequires:	python-pycurl
BuildRequires:	python-pyinotify
BuildRequires:	python-pyparsing
BuildRequires:	python-simplejson
%if %{with initscript}
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
%endif
%if %{with systemd_service}
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun,postun):	systemd-units >= 38
Requires:	systemd-units >= 0.38
%endif
#BuildRequires:	-
#BuildRequires:	autoconf
#BuildRequires:	automake
#BuildRequires:	intltool
#BuildRequires:	libtool
#Requires(postun):	-
#Requires(pre,post):	-
#Requires(preun):	-
#Requires:	-
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Ganeti is a cluster virtual server management software tool built on
top of existing virtualization technologies such as Xen or KVM and
other Open Source software.

%package subpackage
Summary:	-
Summary(pl.UTF-8):	-
Group:		-
# noarch subpackages only when building with rpm5
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description subpackage

%description subpackage -l pl.UTF-8

%package libs
Summary:	-
Summary(pl.UTF-8):	-
Group:		Libraries

%description libs

%description libs -l pl.UTF-8

%package devel
Summary:	Header files for %{name} library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki %{name}
Group:		Development/Libraries
# if base package contains shared library for which these headers are
#Requires:	%{name} = %{version}-%{release}
# if -libs package contains shared library for which these headers are
#Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for %{name} library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki %{name}.

%package static
Summary:	Static %{name} library
Summary(pl.UTF-8):	Statyczna biblioteka %{name}
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static %{name} library.

%description static -l pl.UTF-8
Statyczna biblioteka %{name}.

%prep
%setup -q

%build
# DON'T use full path to xl binary, just 'xl' (see lib/hypervisor/hv_xen.py for a reason)
%configure \
	IP_PATH=/sbin/ip \
	DOT=/usr/bin/dot \
	PYLINT=/usr/bin/pylint \
	SOCAT=/usr/bin/socat \
	QEMUIMG_PATH=/usr/bin/qemu-img \
	--enable-syslog \
	--enable-htools \
	--enable-htools-rapi \
	--enable-confd=python \
	--enable-socat-escape \
	--with-ssh-initscript=/etc/rc.d/init.d/sshd \
	--with-ssh-config-dir=/stc/ssh \
	--with-xen-cmd=xl \
	--with-kvm-path=/usr/bin/qemu-kvm

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%if %{with initscript}
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}
%endif
#install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g xxx %{name}
%useradd -u xxx -d /var/lib/%{name} -g %{name} -c "XXX User" %{name}

%post

%preun

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%if %{with ldconfig}
%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig
%endif

%if %{with initscript}
%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%endif

%if %{with systemd_service}
%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_reload
%endif

%files
%defattr(644,root,root,755)
%doc AUTHORS CREDITS CHANGES ChangeLog NEWS README THANKS TODO

%if 0
# if _sysconfdir != /etc:
#%%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*
%attr(755,root,root) %{_bindir}/%{name}*
%{_datadir}/%{name}
%endif

# initscript and its config
%if %{with initscript}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%endif

%if %{with systemd_service}
%{systemdunitdir}/%{name}.service
%endif

#%{_examplesdir}/%{name}-%{version}

%if %{with subpackage}
%files subpackage
%defattr(644,root,root,755)
#%doc extras/*.gz
#%{_datadir}/%{name}-ext
%endif
