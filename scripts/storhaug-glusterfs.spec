%define major_version 0
%define minor_version 1
%define release 1%{?dist}

Name: storhaug-glusterfs
Summary: High-Availability Storage Server Add-on
Version: %{major_version}.%{minor_version}
Release: %{release}
License: GPLv2+
Group: Applications/System
URL: http://www.redhat.com
Vendor: Red Hat, Inc.
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-root

Source0: %{name}-%{version}.tar.gz

Requires: glusterfs-server
%if %{defined rhel} && %{rhel} < 7
Requires: cman
Requires: pacemaker
%else
Requires: fence-agents-all
%endif
Requires: pcs

%description
High-Availability add-on for storage servers

### NFS (NFS-Ganesha)
%package nfs
Summary: storhaug-glusterfs NFS module
Group: Applications/System
Requires: storhaug-glusterfs = %{version}-%{release}
Requires: nfs-ganesha
Requires: nfs-ganesha-utils

%description nfs
High-Availability NFS add-on for storage servers

### SMB (Samba)
%package smb
Summary: storhaug-glusterfs SMB module
Group: Applications/System
Requires: storhaug-glusterfs = %{version}-%{release}
Requires: ctdb >= 2.5
Requires: samba
Requires: samba-client
Requires: samba-winbind
Requires: samba-winbind-clients

%description smb
High-Availability SMB add-on for storage servers


%prep
%setup -q -n %{name}

%install
%{__rm} -rf %{buildroot}

install -d -m 0755 %{buildroot}%{_sbindir}
install -m 0700 storhaug-glusterfs %{buildroot}%{_sbindir}/storhaug-glusterfs

sed -i 's/\%CONFDIR/\%{_sysconfdir}/' "%{buildroot}%{_sbindir}/storhaug-glusterfs"

install -d -m 0700 %{buildroot}%{_sysconfdir}/sysconfig/storhaug-glusterfs.d
install -m 0600 storhaug-glusterfs.conf.sample %{buildroot}%{_sysconfdir}/sysconfig/storhaug-glusterfs.conf
install -m 0600 nfs-ha.conf.sample %{buildroot}%{_sysconfdir}/sysconfig/storhaug-glusterfs.d/nfs-ha.conf
install -m 0600 smb-ha.conf.sample %{buildroot}%{_sysconfdir}/sysconfig/storhaug-glusterfs.d/smb-ha.conf

install -d -m 0755 %{buildroot}%{_prefix}/lib/ocf/resource.d/heartbeat
install -m 0755 ganesha %{buildroot}%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha
install -m 0755 ganesha_trigger %{buildroot}%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha_trigger

%post
%if %{defined rhel} && %{rhel} < 7
chkconfig corosync off
chkconfig pacemaker on
chkconfig pcsd on
service pcsd start
%else
systemctl start pcsd.service
systemctl enable pcsd.service
%endif


%post smb
%if %{defined rhel} && %{rhel} < 7
chkconfig ctdb off
chkconfig smb off
chkconfig nmb off
chkconfig winbind off
service ctdb stop
service smb stop
service nmb stop
service winbind stop
%else
systemctl stop ctdb smb nmb winbind
systemctl disable ctdb smb nmb winbind
%endif

%post nfs
%if %{defined rhel} && %{rhel} < 7
chkconfig nfs-server off
chkconfig nfs-lock off
service nfs-server stop
service nfs-lock stop
%else
systemctl stop nfs-server nfs-lock
systemctl disable nfs-server nfs-lock
%endif

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/storhaug-glusterfs.conf
%attr(755,root,root) %dir %{_sysconfdir}/sysconfig/storhaug-glusterfs.d/
%{_sbindir}/storhaug-glusterfs

%files nfs
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/storhaug-glusterfs.d/nfs-ha.conf
%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha
%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha_trigger

%files smb
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/storhaug-glusterfs.d/smb-ha.conf


%changelog
* Fri Sep 30 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.13-1
 - Allow CTDB rec_lock to be optional.
 - Use crm_master to determine CTDB rec_master.
 - Remove CTDB lock file volume.

* Sat Sep 24 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.12-1
 - Remove IP address parameter from trigger RA.
 - Trigger grace from notify action.

* Sat Sep 24 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.11-6
 - Update shared state variable names
 - Fix erroneous directory names
 - Fix reverse reference links

* Sat Sep 24 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.11-5
 - Properly detect and source only properly named config files.

* Wed Sep 21 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.11-4
 - Missing copy functions.
 - Prepare function for move to RA.
 - Whitespace fixes.

* Wed Sep 21 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.11-3
 - Allow configuration of the shared state FS type via
   HA_NFS_STATE_FS.

* Wed Sep 21 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.11-2
 - Use helper functions to help simplify long functions.

* Wed May 11 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.11-1
- Overhaul addnode().

* Wed May 11 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.10-4
- Add hook for OCF_DEBUG_LIBRARY in RAs.
- Cache local hostname.
- Various cruft removals.
- Improve cleanup, add cleanup-all.
- Fix copy_config().
- Don't be such a Red Hat.

* Wed May 11 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.10-3
- Parametize NFS-Ganesha config file.
- Do /var/lib/nfs swap in NFS-Ganesha RA.
- Parametize NFS-Ganesha shared state mountpoint.

* Sat Mar 05 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.10-2
- Shorten and clarify copyright notice

* Mon Feb 29 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.10-1
- Major reorganization of main script file
- Provide HA for NFS-Ganesha, based on ganesha-ha

* Mon Feb 29 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.9-2
- Rename some variables and examples
- Label service feature unimplemented

* Fri Jan 29 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.9-1
- Implement deterministic failover
- Based on the version in ganesha-ha

* Sun Jan 24 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.8-6
- Remove uneccessary variables from setup_cluster()
- Allow for configuration of GlusterFS mount points
- Minor cleanups

* Sat Jan 23 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.8-5
- Add a logging function to streamline logging to syslog

* Sat Jan 23 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.8-4
- Largely cosmetic changes to bring storhaug more in line with Ganesha-HA

* Sat Jan 23 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.8-3
- Add an actual usage message under --help/-h

* Wed Jan 20 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.8-2
- Normalize whitespace in main storhaug file.
- Change said file's mode to executable.

* Mon Jan 18 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.8-1
- Rename the project to storhaug
- Remove CTDB RA from source

* Mon Jan 18 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.7-2
- Remove specfile and source tarball from source dir.

* Mon Jan 18 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.7-1
- Force cluster creation
- Allow for definition of which nodes will be storage nodes
- Enable direct-io for GlusterFS backend volumes
- Temporarily comment out NFS functionality

* Thu Nov 19 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.6-2
- Add functionality for EL7

* Thu Apr 23 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.6-1
- Properly update CIB file during cluster creation
- Better tempfile handling
- Improve ganesha statedir creation

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.5-1
- Remove extraneous cleanup commands

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.4-1
- Add missing service
- Add missing requires

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.3-3
- Fix installation config bug

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.3-2
- Don't install custom CTDB RA, update it in
  resource-agents package

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.3-1
- Add storage-ha script
- Additional post-installation prep work

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.2-2
- Add Ganesha symlink

* Mon Apr 13 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.2-1
- Add config files

* Wed Apr 08 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.1-1
- Initial version
