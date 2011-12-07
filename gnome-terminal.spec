%define gettext_package gnome-terminal

%define glib2_version 2.16.0
%define gtk2_version 2.14.0
%define gconf_version 2.14.0
%define vte_version 0.25.1
%define desktop_file_utils_version 0.2.90

Summary: Terminal emulator for GNOME
Name: gnome-terminal
Version: 2.31.3
Release: 4%{?dist}
License: GPLv2+ and GFDL
Group: User Interface/Desktops
URL: http://www.gnome.org/
Source0: http://download.gnome.org/sources/gnome-terminal/2.31/gnome-terminal-%{version}.tar.bz2
# http://bugzilla.gnome.org/show_bug.cgi?id=588732
Source1: profile-new-dialog.ui
# Fix gnome.org Bug 338913 – Terminal resized when switching tabs
Patch2: gnome-terminal-2.15.0-338913-revert-336325.patch

# make docs show up in rarian/yelp
Patch3: gnome-terminal-doc-category.patch

# drop gtk requirement down again
Patch4: gnome-terminal-unseal.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=604207
Patch5: gnome-terminal-tab-dnd-fix.patch

# Translation update
# https://bugzilla.redhat.com/show_bug.cgi?id=575706
Patch6: gnome-terminal-2.31.3-translations.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# gconftool-2
Requires(pre): GConf2 >= %{gconf_version}
Requires(post): GConf2 >= %{gconf_version}
Requires(preun): GConf2 >= %{gconf_version}
Requires(post): scrollkeeper
Requires(postun): scrollkeeper

# needed for GConf schemas
Requires: libgnome

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: GConf2-devel >= %{gconf_version}
BuildRequires: libglade2-devel
BuildRequires: libgnomeui-devel
BuildRequires: vte-devel >= %{vte_version}
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: scrollkeeper
BuildRequires: gettext
BuildRequires: gnome-doc-utils
BuildRequires: intltool


%description
gnome-terminal is a terminal emulator for GNOME. It supports translucent
backgrounds, opening multiple terminals in a single window (tabs) and
clickable URLs.

%prep
%setup -q
%patch2 -p1 -b .338913-revert-336325
%patch3 -p1 -b .doc-category
%patch4 -p1 -R -b .unseal
%patch5 -p1 -b .tab-dnd-fix
%patch6 -p2 -b .translations

%build

#workaround broken perl-XML-Parser on 64bit arches
export PERL5LIB=/usr/lib64/perl5/vendor_perl/5.8.2 perl

%configure --with-widget=vte --disable-scrollkeeper
make %{?_smp_mflags}

cp %{SOURCE1} src

# strip unneeded translations from .mo files
cd po
grep -v ".*[.]desktop[.]in.*\|.*[.]server[.]in$" POTFILES.in > POTFILES.keep
mv POTFILES.keep POTFILES.in
intltool-update --pot
for p in *.po; do
  msgmerge $p %{gettext_package}.pot > $p.out
  msgfmt -o `basename $p .po`.gmo $p.out
done

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

sed -i -e "s/Icon=gnome-terminal.png/Icon=gnome-terminal/" \
  $RPM_BUILD_ROOT%{_datadir}/applications/gnome-terminal.desktop

desktop-file-install --vendor gnome --delete-original	\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications		\
  --remove-category=Application				\
  --add-category=System					\
  $RPM_BUILD_ROOT%{_datadir}/applications/gnome-terminal.desktop

# grr, --disable-scrollkeeper is not good enough
rm -rf $RPM_BUILD_ROOT/var/scrollkeeper

%find_lang %{gettext_package} --with-gnome

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
	%{_sysconfdir}/gconf/schemas/gnome-terminal.schemas > /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-terminal.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-terminal.schemas > /dev/null || :
fi

%postun
scrollkeeper-update -q

%files -f %{gettext_package}.lang
%defattr(-,root,root,-)

%doc AUTHORS COPYING NEWS README

%{_bindir}/gnome-terminal
%{_datadir}/gnome-terminal
%{_datadir}/omf/gnome-terminal
%{_datadir}/applications/gnome-terminal.desktop
%{_sysconfdir}/gconf/schemas/gnome-terminal.schemas

%changelog
* Mon Aug  9 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.31.3-4
- Updated translations (#575706)

* Mon Jun 28 2010 Matthias Clasen <mclasen@redhat.com> - 2.31.3-3
- Fix a crash in tab DND
Resolves: #604207

* Wed May 19 2010 Behdad Esfahbod <behdad@redhat.com> - 2.31.3-2
- Update to 2.31.3
- Resolves: #469930

* Tue May 11 2010 Matthias Clasen <mclasen@redhat.com> - 2.29.6-4
- Updated translations
Resolves: #575706

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> - 2.29.6-3
- Make docs show up in yelp
Resolves: #588571

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> - 2.29.6-2
- Require libgnome
Resolves: #588049

* Thu Jan 14 2010 Behdad Esfahbod <behdad@redhat.com> - 2.29.6-1
- Update to 2.29.6
- Drop stale patch

* Mon Jan  4 2010 Matthias Clasen <mclasen@redhat.com> - 2.28.2-1
- Update to 2.28.2

* Mon Oct 19 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.1-1
- Update to 2.28.1, translation updates

* Mon Oct  5 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- Fix a small memory leak

* Mon Sep 21 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.92-1
- Update to 2.27.92

* Wed Aug 19 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.91-1
- Update to 2.27.91

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.26.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 15 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.2-2
- Fix a stubborn icon

* Wed May 20 2009 Ray Strode <rstrode@redhat.com> 2.26.2-1
- Update to 2.26.2

* Mon Apr 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-2
- Don't drop schemas translations from po files

* Mon Apr 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/gnome-terminal/2.26/gnome-terminal-2.26.1.news

* Wed Apr  8 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-2
- Incorporate upstream patch to make session saving work better

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Jan 20 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.5-1
- Update to 2.25.5

* Wed Dec 17 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.3-2
- Update to 2.25.3

* Tue Nov 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.2-2
- Update to 2.24.2

* Fri Nov 21 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-4
- Tweak %%description

* Thu Nov 20 2008 Behdad Esfahbod <besfahbo@redhat.com> - 2.24.1-3
- Require vte >= 0.17.0
- Resolves: #472330

* Tue Oct 21 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-2
- Make tab switching shortcuts work again

* Mon Oct 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Thu Sep 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-2
- Save some space

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Sat Aug 23 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-2
- Rebuild

* Tue Aug  5 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-1
- Update to 2.23.6

* Wed Jun 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.2-1
- Update to 2.23.4.2

* Wed Jun  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.3.1-1
- Update to 2.23.3.1

* Tue Jun  3 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.3-1
- Update to 2.23.3

* Wed May 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.22.1-2
- fix license tag (GFDL+ is the same as GFDL)

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Tue Feb 26 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Wed Feb 13 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91.1-1
- Update to 2.21.91.1

* Wed Feb 13 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Wed Feb  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-2
- Remove OnlyShowIn from the desktop file  (#258901)

* Wed Jan 30 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Tue Jan 15 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.5-1 
- Update to 2.21.5

* Fri Dec 21 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.4-1
- Update to 2.21.4

* Thu Dec  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.3-1
- Update to 2.21.3

* Tue Nov 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.3-1
- Update to 2.18.3

* Tue Sep 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.2-1
- Update to 2.18.2

* Wed Aug 22 2007 Adam Jackson <ajax@redhat.com> - 2.18.1-3
- Rebuild for PPC toolchain bug
- Fix build for rarian

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.1-2
- Update license field
- Use %%find_lang for help files

* Mon Jun 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.1-1
- Update to 2.18.1

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92

* Thu Feb 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.91-3
- Add System to desktop file categories

* Wed Feb 14 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.91-2
- Package review feedback

* Tue Feb 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.91-1
- Update to 2.17.91

* Tue Jan 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90-1
- Update to 2.17.90

* Sat Oct 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-1
- Update to 2.16.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-3
- Fix scripts according to packaging guidelines

* Fri Sep  8 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-2
- Fix directory ownership issues (#205679)

* Tue Sep  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1.fc6
- Update to 2.16.0

* Wed Aug  2 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.4-1.fc6
- Update to 2.15.4

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.2-1
- Update to 2.15.2

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.15.1-2.1
- rebuild

* Mon May 29 2006 Kristian Høgsberg <krh@redhat.com> - 2.15.1-2
- Update transparency patch to use gdk_screen_is_composited().

* Mon May 22 2006 Matthias Clasen <mclasen@redhat.com> 2.15.1-1
- Update to 2.15.1

* Thu May 18 2006 Dan Williams <dcbw@redhat.com> - 2.15.0-2
- Revert gnome.org #336325 (fixes #338913 – Terminal resized when switching tabs)

* Tue May 16 2006 Matthias Clasen <mclasen@redhat.com> 2.15.0-1
- Update to 2.15.0

* Thu May 11 2006 Matthias Clasen <mclasen@redhat.com> 2.14.1-13
- Close the about dialog

* Wed May 10 2006 Matthias Clasen <mclasen@redhat.com> 2.14.1-12
- Rebuild 

* Tue Apr 25 2006 Kristian Høgsberg <krh@redhat.com> 2.14.1-11
- Bump for rawhide build.

* Tue Apr 25 2006 Kristian Høgsberg <krh@redhat.com> - 2.14.1-10
- Fix selection atom name intialization (patch from Kjartan Maaras).
- Lower vte requirement to 0.12.0-2 which is what fc5-bling has.

* Wed Apr 19 2006 Ray Strode <rstrode@redhat.com> 2.14.1-9
- Require newer vte (bug 189341)

* Tue Apr 18 2006 Kristian Høgsberg <krh@redhat.com> 2.14.1-8
- Bump for rawhide build.

* Tue Apr 18 2006 Kristian Høgsberg <krh@redhat.com> 2.14.1-7
- Only use ARGB visual if a compositing manager is running to avoid
  slow-down caused by automatic compositor.

* Mon Apr 17 2006 Kristian Høgsberg <krh@redhat.com> 2.14.1-6
- Bumpd for rawhide build.

* Mon Apr 17 2006 Kristian Høgsberg <krh@redhat.com> 2.14.1-5
- Fix gnome-terminal-2.14.1-real-transparency.patch to check for
  window->priv != NULL before dereferencing.

* Thu Apr 13 2006 Kristian Høgsberg <krh@redhat.com> 2.14.1-4
- Bump for rawhide build.

* Thu Apr 13 2006 Kristian Høgsberg <krh@redhat.com> 2.14.1-3
- Add gnome-terminal-2.14.1-real-transparency.patch for extra bling points.

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Sat Mar  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.93-1
- Update to 2.13.93

* Sat Mar  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.92-1
- Update to 2.13.92

* Sun Feb 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.91-1
- Update to 2.13.91

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-2.1
- bump again for double-long bug on ppc(64)

* Thu Feb  9 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.90-2
- Re-add "Open Link" menuitems

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 30 2006 Christopher Aillon <caillon@redhat.com> 2.13.90-1
- Update to 2.13.90
- Add patch to not specify a default invisible char, let GTK+ handle it

* Thu Jan 19 2006 Matthias Clasen <mclasen@redhat.com> 2.13.3-1
- Update to 2.13.3

* Tue Jan 17 2006 Matthias Clasen <mclasen@redhat.com> 2.13.2-1
- Update to 2.13.2

* Fri Jan 13 2006 Matthias Clasen <mclasen@redhat.com> 2.13.1-1
- Update to 2.13.1
- Remove upstreamed patches

* Thu Jan  4 2006 Christopher Aillon <caillon@redhat.com> 2.13.0-2
- Revert patch from gnome bug 98715 to fix 176029, 176642

* Thu Dec 15 2005 Matthias Clasen <mclasen@redhat.com> 2.13.0-1
- Update to 2.13.0

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Nov 28 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0-2
- Respect the show_input_method_menu setting.

* Thu Sep  8 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0-1
- Update to 2.12.0

* Tue Aug 16 2005 Warren Togami <wtogami@redhat.com> - 2.11.2-1
- rebuild for new cairo and 2.11.2

* Mon Jul 11 2005 Matthias Clasen <mclasen@redhat.com> 2.11.1-1
- Newer upstream version

* Wed May 4 2005 Ray Strode <rstrode@redhat.com> 2.10.0-2
- Fix ne translation (bug 152240).

* Fri Mar 25 2005 Christopher Aillon <caillon@redhat.com> 2.10.0-1
- Update to 2.10.0

* Wed Feb  2 2005 Matthias Clasen <mclasen@redhat.com> 2.9.2-1
- Update to 2.9.2

* Thu Nov  4 2004 Ray Strode <rstrode@redhat.com> 2.8.0-2
- rebuild for rawhide

* Thu Nov  4 2004 Ray Strode <rstrode@redhat.com> 2.8.0-1
- Update to 2.8.0 (bug #136034)

* Fri Jul 30 2004 Ray Strode <rstrode@redhat.com> 2.7.3-1
- Update to 2.7.3

* Fri Jun 18 2004 Ray Strode <rstrode@redhat.com> 2.6.0-4
- patch a build busting type mismatch in libegg files

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Apr 13 2004 Warren Togami <wtogami@redhat.com> 2.6.0-2
- #111015 BR scrollkeeper gettext

* Wed Mar 31 2004 Mark McLoughlin <markmc@redhat.com> 2.6.0-1
- Update to 2.6.0

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 25 2004 Alexander Larsson <alexl@redhat.com> 2.5.90-1
- update to 2.5.90

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jan 26 2004 Alexander Larsson <alexl@redhat.com> 2.5.1-1
- update to 2.5.1

* Wed Sep 17 2003 Alexander Larsson <alexl@redhat.com> 2.4.0.1-1
- update to 2.4.0.1

* Fri Aug 15 2003 Alexander Larsson <alexl@redhat.com> 2.3.1-1
- update to gnome 2.3

* Mon Jul 28 2003 Havoc Pennington <hp@redhat.com> 2.2.2-2
- rebuild

* Mon Jul  7 2003 Havoc Pennington <hp@redhat.com> 2.2.2-1
- 2.2.2
- require latest vte

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 14 2003 Havoc Pennington <hp@redhat.com> 2.2.1-3
- remove Xft buildreq

* Thu Feb  6 2003 Jeremy Katz <katzj@redhat.com> 2.2.1-2
- confusion about build roots abounds...

* Wed Feb  5 2003 Havoc Pennington <hp@redhat.com> 2.2.1-1
- 2.2.1

* Sun Jan 26 2003 Havoc Pennington <hp@redhat.com>
- require gtk 2.2, pango 1.2

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 21 2003 Havoc Pennington <hp@redhat.com>
- 2.2.0

* Fri Jan 10 2003 Havoc Pennington <hp@redhat.com>
- 2.1.4

* Tue Dec 10 2002 Havoc Pennington <hp@redhat.com>
- merge nalin's branch to HEAD, bump some dependency versions

* Tue Dec 10 2002 Nalin Dahyabhai <nalin@redhat.com> 2.1.3-0
- initial update to 2.1.3

* Tue Dec 10 2002 Tim Powers <timp@redhat.com> 2.0.1-6
- rebuild to fix broken deps on old libvte
- build on all arches

* Mon Sep  2 2002 Nalin Dahyabhai <nalin@redhat.com> 2.0.1-5
- fix goofy audible bell checkbox (backport from HEAD)

* Mon Sep  2 2002 Nalin Dahyabhai <nalin@redhat.com> 2.0.1-4
- fix incorrect regexp which matched newlines as parts of URLs (#71349)

* Fri Aug 23 2002 Jonathan Blandford <jrb@redhat.com>
- Clean up keyboard handling.

* Tue Aug 13 2002 Havoc Pennington <hp@redhat.com>
- require latest vte

* Thu Aug  8 2002 Havoc Pennington <hp@redhat.com>
- 2.0.1 released version instead of cvs snap
- clean up unpackaged files

* Thu Aug  8 2002 Nalin Dahyabhai <nalin@redhat.com>
- pick up widget padding

* Wed Jul 24 2002 Owen Taylor <otaylor@redhat.com>
- Use monospace preference for system font

* Thu Jul 18 2002 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Fri Jul 12 2002 Havoc Pennington <hp@redhat.com>
- 2.0.0.90 cvs snap

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Jun 17 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Mon Jun 17 2002 Havoc Pennington <hp@redhat.com>
- 2.0.0
- use desktop-file-install
- put bonobo server file in file list
- put help files in file list
- apply some fixes from CVS (or rather, that I'm going to 
  check in to CVS soon)

* Fri Jun 14 2002 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in different environment

* Fri Jun 14 2002 Nalin Dahyabhai <nalin@redhat.com>
- add patch to handle vte abi change

* Tue Jun 11 2002 Havoc Pennington <hp@redhat.com>
- add patch to get a decent default monospace font

* Mon Jun 10 2002 Havoc Pennington <hp@redhat.com>
- rebuild, had bin compat issues

* Sun Jun 09 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Sun Jun  9 2002 Havoc Pennington <hp@redhat.com>
- don't obsolete/provide gnome-core

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- 1.9.7

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment
- build requires bonobo activation

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 1.9.6.90
- provide gnome-core

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- 1.9.5
- obsolete gnome-core

* Fri Apr 26 2002 Havoc Pennington <hp@redhat.com>
- 1.9.4.91, fixes scrollback thing

* Thu Apr 25 2002 Havoc Pennington <hp@redhat.com>
- 1.9.4.90
- move it to VTE, let's see how this goes

* Tue Apr 16 2002 Havoc Pennington <hp@redhat.com>
- Initial build.


