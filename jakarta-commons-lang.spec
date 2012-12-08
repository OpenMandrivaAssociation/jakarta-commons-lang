# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support        0

%define base_name       lang
%define short_name      commons-%{base_name}

Name:           jakarta-%{short_name}
Version:        2.3
Release:        2.3.6
Epoch:          0
Summary:        Provides a host of helper utilities for the java.lang API
License:        Apache License
Group:          Development/Java

URL:            http://commons.apache.org/lang/
Source0:        http://www.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        %{short_name}-%{version}-jpp-depmap.xml
Source5:        %{short_name}-%{version}.pom
Patch0:         %{name}-notarget.patch
Patch1:         %{name}-addosgimanifest.patch

%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
BuildRequires:  java-devel
%endif
BuildRequires:  ant
BuildRequires:  java-rpmbuild
%if %with tests
BuildRequires:  ant-junit
BuildRequires:  junit
%endif

%description
The standard Java libraries fail to provide enough methods for
manipulation of its core classes. The Commons Lang Component provides
these extra methods.
The Commons Lang Component provides a host of helper utilities for the
java.lang API, notably String manipulation methods, basic numerical
methods, object reflection, creation and serialization, and System
properties. Additionally it contains an inheritable enum type, an
exception structure that supports multiple types of nested-Exceptions
and a series of utlities dedicated to help with building methods, such
as hashCode, toString and equals.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
BuildRequires:  java-javadoc

%description    javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{short_name}-%{version}-src
%{__perl} -pi -e 's/\r//g' *.txt
%{__sed} -i 's/\r//' STATUS.html

if [ ! -f %{SOURCE4} ]; then
export DEPCAT=$(pwd)/%{short_name}-%{version}-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > %{short_name}-%{version}-depmap.new.xml
fi
%patch0
%patch1

%build
# FIXME: There are failures with gcj. Ignore them for now.
%if %{gcj_support}
  %ant \
    -Djunit.jar=$(find-jar junit) \
    -Dfinal.name=%{short_name} \
    -Djdk.javadoc=%{_javadocdir}/java \
    -Dtest.failonerror=false \
    jar javadoc
%else
  %ant \
    -Djunit.jar=$(find-jar junit) \
    -Dfinal.name=%{short_name} \
    -Djdk.javadoc=%{_javadocdir}/java \
    jar javadoc
%endif
#    test dist

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}
cp -a dist/%{short_name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `echo $jar| %{__sed} "s|jakarta-||g"`; done)
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `echo $jar| %{__sed} "s|-%{version}||g"`; done)

%add_to_maven_depmap %{base_name} %{base_name} %{version} JPP %{name}

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -m 644 %{SOURCE5} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -a dist/docs/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%{__perl} -pi -e 's/\r$//g' *.html *.txt

## manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -p STATUS.html $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -p *.txt $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%{gcj_compile}

%clean
%{__rm} -rf %{buildroot}

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%dir %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/STATUS.html
%doc %{_docdir}/%{name}-%{version}/*.txt
#%doc PROPOSAL.html STATUS.html LICENSE.txt NOTICE.txt RELEASE-NOTES.txt
%{_javadir}/*
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-*%{version}.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}


%changelog
* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0:2.3-2.3.5mdv2011.0
+ Revision: 606056
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:2.3-2.3.4mdv2010.1
+ Revision: 522979
- rebuilt for 2010.1

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 0:2.3-2.3.3mdv2010.0
+ Revision: 425438
- rebuild

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 0:2.3-2.3.2mdv2009.1
+ Revision: 351284
- rebuild

* Sun Aug 10 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:2.3-2.3.1mdv2009.0
+ Revision: 270131
- add OSGi manifest/sync with fedora

* Thu Feb 14 2008 Thierry Vignaud <tv@mandriva.org> 0:2.3-1.0.2mdv2009.0
+ Revision: 167945
- fix no-buildroot-tag
- kill re-definition of %%buildroot on Pixel's request

  + Anssi Hannula <anssi@mandriva.org>
    - buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Mon Dec 10 2007 Alexander Kurtakov <akurtakov@mandriva.org> 0:2.3-1.0.1mdv2008.1
+ Revision: 116870
- add maven poms (jpp sync)

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:2.3-0.0.2mdv2008.0
+ Revision: 87411
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Wed Jul 11 2007 David Walluck <walluck@mandriva.org> 0:2.3-0.0.1mdv2008.0
+ Revision: 51167
- 2.3
- Import jakarta-commons-lang




* Sat Jul 22 2006 David Walluck <walluck@mandriva.org> 0:2.1-4.1mdv2006.0
- bump release

* Thu Jun 01 2006 David Walluck <walluck@mandriva.org> 0:2.1-1.2mdv2006.0
- rebuild for libgcj.so.7
- own %%{_libdir}/gcj/%%{name}

* Fri Dec 02 2005 David Walluck <walluck@mandriva.org> 0:2.1-1.1mdk
- sync with 2.1-1jpp

* Sat May 21 2005 David Walluck <walluck@mandriva.org> 0:2.0-2.1mdk
- release

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:2.0-2jpp
- Rebuild with ant-1.6.2

* Sun Oct 12 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-1jpp
- Update to 2.0.
- Add non-versioned javadocs dir symlink.
- Crosslink with local J2SE javadocs.
- Convert specfile to UTF-8.

* Fri Apr  4 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0.1-3jpp
- Rebuild for JPackage 1.5.

* Tue Mar  4 2003 Ville Skyttä <ville.skytta at iki.fi> - 1.0.1-2jpp
- Repackage to recover from earlier accidental overwrite with older version.
- No macros in URL and SourceX tags.
- Remove spurious api/ from installed javadoc path.
- Spec file cleanups.
- (from 1.0.1-1jpp) Update to 1.0.1.
- (from 1.0.1-1jpp) Run JUnit tests when building.

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0-3jpp
- fix ASF license and add packager tag

* Mon Oct 07 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-2jpp
- missed to include changelog

* Mon Oct 07 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-1jpp
- release 1.0

* Tue Aug 20 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0.b1.1-1jpp
- fist jpp release
