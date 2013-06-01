Summary:	Cluster-based virtualization management software
Name:		ganeti
Version:	2.6.2
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	https://ganeti.googlecode.com/files/%{name}-%{version}.tar.gz
# Source0-md5:	9d9a0c5c0341d5775988961449f82b99
Source1:	%{name}.tmpfiles
Patch0:		fix-no-kvm.patch
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
BuildRequires:	python-devel
BuildRequires:	python-distribute
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	rc-scripts
Requires:	systemd-units >= 0.38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Ganeti is a cluster virtual server management software tool built on
top of existing virtualization technologies such as Xen or KVM and
other Open Source software.

%package htools
Summary:	Cluster allocation tools for Ganeti
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description htools
These are additional tools used for enhanced allocation and capacity
calculation on Ganeti clusters.

The tools provided are:
 - hail, an iallocator script for ganeti
 - hbal, used to redistribute instances on the cluster
 - hspace, used for capacity calculation
 - hscan, used to gather cluster files for offline use in hbal/hspace

%prep
%setup -q
%patch0 -p1

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
install -d $RPM_BUILD_ROOT{%{systemdunitdir},%{systemdtmpfilesdir}} \
	$RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/ganeti.conf

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
%pre
%groupadd -g xxx %{name}
%useradd -u xxx -d /var/lib/%{name} -g %{name} -c "XXX User" %{name}

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi
%endif

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc NEWS README UPGRADE
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{systemdunitdir}/%{name}.service
%{systemdtmpfilesdir}/ganeti.conf
%if 0
# if _sysconfdir != /etc:
#%%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*
%endif
%dir %{_libdir}/ganeti
%{_libdir}/ganeti/check-cert-expired
%{_libdir}/ganeti/daemon-util
%{_libdir}/ganeti/ensure-dirs
%{_libdir}/ganeti/import-export
%{_libdir}/ganeti/kvm-ifup
%dir %{_libdir}/ganeti/iallocators
%dir %{_libdir}/ganeti/tools
%{_libdir}/ganeti/tools/burnin
%{_libdir}/ganeti/tools/cfgshell
%{_libdir}/ganeti/tools/cfgupgrade
%{_libdir}/ganeti/tools/cfgupgrade12
%{_libdir}/ganeti/tools/cluster-merge
%{_libdir}/ganeti/tools/confd-client
%{_libdir}/ganeti/tools/fmtjson
%{_libdir}/ganeti/tools/kvm-console-wrapper
%{_libdir}/ganeti/tools/lvmstrap
%{_libdir}/ganeti/tools/master-ip-setup
%{_libdir}/ganeti/tools/move-instance
%{_libdir}/ganeti/tools/ovfconverter
%{_libdir}/ganeti/tools/sanitize-config
%{_libdir}/ganeti/tools/setup-ssh
%{_libdir}/ganeti/tools/xen-console-wrapper
%attr(755,root,root) %{_sbindir}/ganeti-cleaner
%attr(755,root,root) %{_sbindir}/ganeti-confd
%attr(755,root,root) %{_sbindir}/ganeti-listrunner
%attr(755,root,root) %{_sbindir}/ganeti-masterd
%attr(755,root,root) %{_sbindir}/ganeti-noded
%attr(755,root,root) %{_sbindir}/ganeti-rapi
%attr(755,root,root) %{_sbindir}/ganeti-watcher
%attr(755,root,root) %{_sbindir}/gnt-backup
%attr(755,root,root) %{_sbindir}/gnt-cluster
%attr(755,root,root) %{_sbindir}/gnt-debug
%attr(755,root,root) %{_sbindir}/gnt-group
%attr(755,root,root) %{_sbindir}/gnt-instance
%attr(755,root,root) %{_sbindir}/gnt-job
%attr(755,root,root) %{_sbindir}/gnt-node
%attr(755,root,root) %{_sbindir}/gnt-os
%{_mandir}/man7/ganeti-os-interface.7*
%{_mandir}/man7/ganeti.7*
%{_mandir}/man8/ganeti-cleaner.8*
%{_mandir}/man8/ganeti-confd.8*
%{_mandir}/man8/ganeti-listrunner.8*
%{_mandir}/man8/ganeti-masterd.8*
%{_mandir}/man8/ganeti-noded.8*
%{_mandir}/man8/ganeti-rapi.8*
%{_mandir}/man8/ganeti-watcher.8*
%{_mandir}/man8/gnt-backup.8*
%{_mandir}/man8/gnt-cluster.8*
%{_mandir}/man8/gnt-debug.8*
%{_mandir}/man8/gnt-group.8*
%{_mandir}/man8/gnt-instance.8*
%{_mandir}/man8/gnt-job.8*
%{_mandir}/man8/gnt-node.8*
%{_mandir}/man8/gnt-os.8*
%dir %{py_sitescriptdir}/ganeti
%{py_sitescriptdir}/ganeti/*.py*
%dir %{py_sitescriptdir}/ganeti/client
%{py_sitescriptdir}/ganeti/client/*.py*
%dir %{py_sitescriptdir}/ganeti/confd
%{py_sitescriptdir}/ganeti/confd/*.py*
%dir %{py_sitescriptdir}/ganeti/http
%{py_sitescriptdir}/ganeti/http/*.py*
%dir %{py_sitescriptdir}/ganeti/hypervisor
%{py_sitescriptdir}/ganeti/hypervisor/*.py*
%dir %{py_sitescriptdir}/ganeti/impexpd
%{py_sitescriptdir}/ganeti/impexpd/*.py*
%dir %{py_sitescriptdir}/ganeti/masterd
%{py_sitescriptdir}/ganeti/masterd/*.py*
%dir %{py_sitescriptdir}/ganeti/rapi
%{py_sitescriptdir}/ganeti/rapi/*.py*
%dir %{py_sitescriptdir}/ganeti/server
%{py_sitescriptdir}/ganeti/server/*.py*
%dir %{py_sitescriptdir}/ganeti/tools
%{py_sitescriptdir}/ganeti/tools/*.py*
%dir %{py_sitescriptdir}/ganeti/utils
%{py_sitescriptdir}/ganeti/utils/*.py*
%dir %{py_sitescriptdir}/ganeti/watcher
%{py_sitescriptdir}/ganeti/watcher/*.py*

%files htools
%defattr(644,root,root,755)
%{_bindir}/hbal
%{_bindir}/hcheck
%{_bindir}/hinfo
%{_bindir}/hscan
%{_bindir}/hspace
%{_bindir}/htools
%{_libdir}/ganeti/iallocators/hail
%{_mandir}/man1/hail.1*
%{_mandir}/man1/hbal.1*
%{_mandir}/man1/hcheck.1*
%{_mandir}/man1/hinfo.1*
%{_mandir}/man1/hscan.1*
%{_mandir}/man1/hspace.1*
%{_mandir}/man1/htools.1*
