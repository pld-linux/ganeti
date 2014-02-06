Summary:	Cluster-based virtualization management software
Name:		ganeti
Version:	2.9.3
Release:	0.7
License:	GPL v2
Group:		Applications/System
Source0:	http://downloads.ganeti.org/releases/2.9/%{name}-%{version}.tar.gz
# Source0-md5:	0542ca872bf2d57284359fcc8dc565ef
Source1:	%{name}.tmpfiles
Source2:	%{name}-confd.init
Source3:	%{name}-masterd.init
Source4:	%{name}-noded.init
Source5:	%{name}-rapi.init
Source6:	%{name}-luxid.init
Source7:	%{name}-mond.init
Source8:	%{name}.sysconfig
Patch0:		fix-no-kvm.patch
Patch1:		systemd.patch
Patch2:		daemon-util-use-service.patch
Patch3:		mtl.patch
Patch4:		use-vm-openvswitch-link.patch
URL:		https://code.google.com/p/ganeti/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	curl-devel
BuildRequires:	fakeroot
BuildRequires:	gawk
BuildRequires:	ghc
BuildRequires:	ghc-Crypto
BuildRequires:	ghc-QuickCheck
BuildRequires:	ghc-curl
BuildRequires:	ghc-haskell-platform
BuildRequires:	ghc-hinotify
BuildRequires:	ghc-hslogger >= 1.2.3
BuildRequires:	ghc-json
BuildRequires:	ghc-regex-pcre
BuildRequires:	ghc-snap-server
BuildRequires:	ghc-temporary
BuildRequires:	ghc-utf8-string
BuildRequires:	gmp-devel
BuildRequires:	hlint
BuildRequires:	hscolour
BuildRequires:	pandoc
BuildRequires:	python
BuildRequires:	python-affinity
BuildRequires:	python-bitarray
BuildRequires:	python-coverage
BuildRequires:	python-devel
BuildRequires:	python-distribute
BuildRequires:	python-ipaddr
BuildRequires:	python-mock >= 1.0.1
BuildRequires:	python-modules
BuildRequires:	python-paramiko
BuildRequires:	python-pep8
BuildRequires:	python-pyOpenSSL
BuildRequires:	python-pycurl
BuildRequires:	python-pyinotify
BuildRequires:	python-pyparsing
BuildRequires:	python-simplejson
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	bridge-utils
Requires:	drbdsetup >= 8.0.12
Requires:	iproute2
Requires:	iputils-arping
Requires:	lvm2
Requires:	openssh-clients
Requires:	openssh-server
Requires:	python
Requires:	python-affinity
Requires:	python-bitarray
Requires:	python-devel
Requires:	python-distribute
Requires:	python-ipaddr
Requires:	python-modules
Requires:	python-paramiko
Requires:	python-pycurl
Requires:	python-pyinotify
Requires:	python-pyOpenSSL
Requires:	python-pyparsing
Requires:	python-simplejson
Requires:	rc-scripts
Requires:	socat
Requires:	sudo
Requires:	systemd-units >= 0.38
#Suggests:	ganeti-instance-debootstrap
Suggests:	qemu
Suggests:	xen
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

%package -n bash-completion-ganeti
Summary:	bash-completion for ganeti
Group:		Applications/Shells
Requires:	%{name} = %{version}

%description -n bash-completion-ganeti
bash-completion for ganeti.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%{__aclocal} -I autotools
%{__autoconf}
%{__automake}
# DON'T use full path to xl binary, just 'xl' (see lib/hypervisor/hv_xen.py for a reason)
%configure \
	IP_PATH=/sbin/ip \
	DOT=/usr/bin/dot \
	PYCOVERAGE=/usr/bin/coverage-%{py_ver} \
	PYLINT=/usr/bin/pylint \
	SOCAT=/usr/bin/socat \
	QEMUIMG_PATH=/usr/bin/qemu-img \
	--enable-syslog \
	--enable-confd \
	--enable-monitoring \
	--enable-socat-escape \
	--with-ssh-initscript=/etc/rc.d/init.d/sshd \
	--with-ssh-config-dir=/etc/ssh \
	--with-kvm-path=/usr/bin/qemu-kvm \
	--enable-restricted-commands \
	--with-user-prefix="gnt-" \
	--with-group-prefix="gnt-" \
	--with-export-dir=/var/lib/ganeti/export \
	--with-iallocator-search-path=%{_libdir}/ganeti/iallocators \
	--with-os-search-path=/srv/ganeti/os,%{_libdir}/ganeti/os,%{_datadir}/ganeti/os \
	--with-extstorage-search-path=/srv/ganeti/extstorage,%{_libdir}/ganeti/extstorage,%{_datadir}/ganeti/extstorage

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{systemdunitdir},%{systemdtmpfilesdir}} \
	$RPM_BUILD_ROOT/etc/{ganeti,cron.d,bash_completion.d,sysconfig,rc.d/init.d,sudoers.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_libdir},%{_datadir}}/ganeti/{os,extstorage}

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/ganeti.conf
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/ganeti-confd
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/ganeti-masterd
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/rc.d/init.d/ganeti-noded
install -p %{SOURCE5} $RPM_BUILD_ROOT/etc/rc.d/init.d/ganeti-rapi
install -p %{SOURCE6} $RPM_BUILD_ROOT/etc/rc.d/init.d/ganeti-luxid
install -p %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/ganeti-mond

%{__sed} -i -e 's|@LIBDIR@|%{_libdir}|g' $RPM_BUILD_ROOT/etc/rc.d/init.d/ganeti-*

cp -p %{SOURCE8} $RPM_BUILD_ROOT/etc/sysconfig/ganeti

cp -p doc/examples/bash_completion $RPM_BUILD_ROOT/etc/bash_completion.d/ganeti
cp -p doc/examples/ganeti.cron $RPM_BUILD_ROOT/etc/cron.d/ganeti
cp -p doc/examples/ganeti.target $RPM_BUILD_ROOT%{systemdunitdir}
cp -p doc/examples/ganeti-{noded,masterd,rapi,confd,luxid,mond}.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p doc/examples/ganeti.sudoers $RPM_BUILD_ROOT/etc/sudoers.d/ganeti

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 300 gnt-masterd
%groupadd -g 301 gnt-confd
%groupadd -g 302 gnt-luxid
%groupadd -g 303 gnt-rapi
%groupadd -g 304 gnt-daemons
%groupadd -g 305 gnt-admin
%useradd -u 300 -d /var/lib/ganeti -g gnt-masterd -G gnt-daemons,gnt-confd,gnt-admin -c "Ganeti Masterd User" gnt-masterd
%useradd -u 301 -d /var/lib/ganeti -g gnt-confd -G gnt-daemons -c "Ganeti Confd User" gnt-confd
%useradd -u 302 -d /var/lib/ganeti -g gnt-luxid -G gnt-daemons,gnt-confd,gnt-masterd -c "Ganeti Luxid User" gnt-luxid
%useradd -u 303 -d /var/lib/ganeti -g gnt-rapi -G gnt-daemons,gnt-admin -c "Ganeti RAPI User" gnt-rapi

%post
/sbin/chkconfig --add ganeti-noded
%service ganeti-noded restart
/sbin/chkconfig --add ganeti-masterd
%service ganeti-masterd restart
/sbin/chkconfig --add ganeti-rapi
%service ganeti-rapi restart
/sbin/chkconfig --add ganeti-confd
%service ganeti-confd restart
/sbin/chkconfig --add ganeti-luxid
%service ganeti-luxid restart
/sbin/chkconfig --add ganeti-mond
%service ganeti-mond restart
%systemd_post ganeti.target ganeti-noded.service ganeti-masterd.service ganeti-rapi.service ganeti-confd.service ganeti-luxid.service ganeti-mond.service

%preun
if [ "$1" = "0" ]; then
	%service -q ganeti-confd stop
	/sbin/chkconfig --del ganeti-confd
	%service -q ganeti-rapi stop
	/sbin/chkconfig --del ganeti-rapi
	%service -q ganeti-masterd stop
	/sbin/chkconfig --del ganeti-masterd
	%service -q ganeti-noded stop
	/sbin/chkconfig --del ganeti-noded
	%service -q ganeti-luxid stop
	/sbin/chkconfig --del ganeti-luxid
	%service -q ganeti-mond stop
	/sbin/chkconfig --del ganeti-mond
fi
%systemd_preun ganeti.target ganeti-noded.service ganeti-masterd.service ganeti-rapi.service ganeti-confd.service ganeti-luxid.service ganeti-mond.service

%postun
if [ "$1" = "0" ]; then
	%userremove gnt-rapi
	%userremove gnt-luxid
	%userremove gnt-confd
	%userremove gnt-masterd
	%groupremove gnt-admin
	%groupremove gnt-masterd
	%groupremove gnt-rapi
	%groupremove gnt-luxid
	%groupremove gnt-confd
	%groupremove gnt-daemons
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc NEWS README UPGRADE
%attr(754,root,root) /etc/rc.d/init.d/ganeti-confd
%attr(754,root,root) /etc/rc.d/init.d/ganeti-luxid
%attr(754,root,root) /etc/rc.d/init.d/ganeti-masterd
%attr(754,root,root) /etc/rc.d/init.d/ganeti-mond
%attr(754,root,root) /etc/rc.d/init.d/ganeti-noded
%attr(754,root,root) /etc/rc.d/init.d/ganeti-rapi
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ganeti
%config(noreplace) %verify(not md5 mtime size) /etc/sudoers.d/ganeti
%dir %{_sysconfdir}/ganeti
%{systemdunitdir}/ganeti.target
%{systemdunitdir}/ganeti-confd.service
%{systemdunitdir}/ganeti-luxid.service
%{systemdunitdir}/ganeti-masterd.service
%{systemdunitdir}/ganeti-mond.service
%{systemdunitdir}/ganeti-noded.service
%{systemdunitdir}/ganeti-rapi.service
%{systemdtmpfilesdir}/ganeti.conf
/etc/cron.d/ganeti
%dir %{_datadir}/ganeti
%dir %{_datadir}/ganeti/extstorage
%dir %{_datadir}/ganeti/os
%dir %{_libdir}/ganeti
%attr(755,root,root) %{_libdir}/ganeti/check-cert-expired
%attr(755,root,root) %{_libdir}/ganeti/daemon-util
%attr(755,root,root) %{_libdir}/ganeti/ensure-dirs
%attr(755,root,root) %{_libdir}/ganeti/import-export
%attr(755,root,root) %{_libdir}/ganeti/kvm-ifup
%attr(755,root,root) %{_libdir}/ganeti/mon-collector
%attr(755,root,root) %{_libdir}/ganeti/node-daemon-setup
%attr(755,root,root) %{_libdir}/ganeti/net-common
%attr(755,root,root) %{_libdir}/ganeti/prepare-node-join
%attr(755,root,root) %{_libdir}/ganeti/vif-ganeti
%dir %{_libdir}/ganeti/extstorage
%dir %{_libdir}/ganeti/iallocators
%dir %{_libdir}/ganeti/os
%dir %{_libdir}/ganeti/tools
%attr(755,root,root) %{_libdir}/ganeti/tools/burnin
%attr(755,root,root) %{_libdir}/ganeti/tools/cfgshell
%attr(755,root,root) %{_libdir}/ganeti/tools/cfgupgrade
%attr(755,root,root) %{_libdir}/ganeti/tools/cfgupgrade12
%attr(755,root,root) %{_libdir}/ganeti/tools/cluster-merge
%attr(755,root,root) %{_libdir}/ganeti/tools/confd-client
%attr(755,root,root) %{_libdir}/ganeti/tools/fmtjson
%attr(755,root,root) %{_libdir}/ganeti/tools/kvm-console-wrapper
%attr(755,root,root) %{_libdir}/ganeti/tools/lvmstrap
%attr(755,root,root) %{_libdir}/ganeti/tools/master-ip-setup
%attr(755,root,root) %{_libdir}/ganeti/tools/move-instance
%attr(755,root,root) %{_libdir}/ganeti/tools/node-cleanup
%attr(755,root,root) %{_libdir}/ganeti/tools/ovfconverter
%attr(755,root,root) %{_libdir}/ganeti/tools/sanitize-config
%attr(755,root,root) %{_libdir}/ganeti/tools/users-setup
%attr(755,root,root) %{_libdir}/ganeti/tools/vcluster-setup
%attr(755,root,root) %{_libdir}/ganeti/tools/xen-console-wrapper
%attr(755,root,root) %{_sbindir}/ganeti-cleaner
%attr(755,root,root) %{_sbindir}/ganeti-confd
%attr(755,root,root) %{_sbindir}/ganeti-listrunner
%attr(755,root,root) %{_sbindir}/ganeti-luxid
%attr(755,root,root) %{_sbindir}/ganeti-masterd
%attr(755,root,root) %{_sbindir}/ganeti-mond
%attr(755,root,root) %{_sbindir}/ganeti-noded
%attr(755,root,root) %{_sbindir}/ganeti-rapi
%attr(755,root,root) %{_sbindir}/ganeti-watcher
%attr(755,root,root) %{_sbindir}/gnt-backup
%attr(755,root,root) %{_sbindir}/gnt-cluster
%attr(755,root,root) %{_sbindir}/gnt-debug
%attr(755,root,root) %{_sbindir}/gnt-group
%attr(755,root,root) %{_sbindir}/gnt-instance
%attr(755,root,root) %{_sbindir}/gnt-job
%attr(755,root,root) %{_sbindir}/gnt-network
%attr(755,root,root) %{_sbindir}/gnt-node
%attr(755,root,root) %{_sbindir}/gnt-os
%attr(755,root,root) %{_sbindir}/gnt-storage
%{_mandir}/man7/ganeti.7*
%{_mandir}/man7/ganeti-extstorage-interface.7*
%{_mandir}/man7/ganeti-os-interface.7*
%{_mandir}/man7/mon-collector.7*
%{_mandir}/man8/ganeti-cleaner.8*
%{_mandir}/man8/ganeti-confd.8*
%{_mandir}/man8/ganeti-listrunner.8*
%{_mandir}/man8/ganeti-luxid.8*
%{_mandir}/man8/ganeti-masterd.8*
%{_mandir}/man8/ganeti-mond.8*
%{_mandir}/man8/ganeti-noded.8*
%{_mandir}/man8/ganeti-rapi.8*
%{_mandir}/man8/ganeti-watcher.8*
%{_mandir}/man8/gnt-backup.8*
%{_mandir}/man8/gnt-cluster.8*
%{_mandir}/man8/gnt-debug.8*
%{_mandir}/man8/gnt-group.8*
%{_mandir}/man8/gnt-instance.8*
%{_mandir}/man8/gnt-job.8*
%{_mandir}/man8/gnt-network.8*
%{_mandir}/man8/gnt-node.8*
%{_mandir}/man8/gnt-os.8*
%{_mandir}/man8/gnt-storage.8*
%dir %{py_sitescriptdir}/ganeti
%{py_sitescriptdir}/ganeti/*.py*
%dir %{py_sitescriptdir}/ganeti/client
%{py_sitescriptdir}/ganeti/client/*.py*
%dir %{py_sitescriptdir}/ganeti/cmdlib
%{py_sitescriptdir}/ganeti/cmdlib/*.py*
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
%dir %{py_sitescriptdir}/ganeti/storage
%{py_sitescriptdir}/ganeti/storage/*.py*
%dir %{py_sitescriptdir}/ganeti/tools
%{py_sitescriptdir}/ganeti/tools/*.py*
%dir %{py_sitescriptdir}/ganeti/utils
%{py_sitescriptdir}/ganeti/utils/*.py*
%dir %{py_sitescriptdir}/ganeti/watcher
%{py_sitescriptdir}/ganeti/watcher/*.py*

%files htools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/harep
%attr(755,root,root) %{_bindir}/hbal
%attr(755,root,root) %{_bindir}/hcheck
%attr(755,root,root) %{_bindir}/hinfo
%attr(755,root,root) %{_bindir}/hroller
%attr(755,root,root) %{_bindir}/hscan
%attr(755,root,root) %{_bindir}/hspace
%attr(755,root,root) %{_bindir}/htools
%attr(755,root,root) %{_libdir}/ganeti/iallocators/hail
%{_mandir}/man1/hail.1*
%{_mandir}/man1/harep.1*
%{_mandir}/man1/hbal.1*
%{_mandir}/man1/hcheck.1*
%{_mandir}/man1/hinfo.1*
%{_mandir}/man1/hroller.1*
%{_mandir}/man1/hscan.1*
%{_mandir}/man1/hspace.1*
%{_mandir}/man1/htools.1*

%files -n bash-completion-ganeti
%defattr(644,root,root,755)
/etc/bash_completion.d/ganeti
