%define gcj_support	1
%define base_name       lang
%define short_name      commons-%{base_name}
%define name            jakarta-%{short_name}
%define section         free
%define build_tests     0

Name:           %{name}
Version:        2.1
Release:        %mkrel 4.1
Epoch:          0
Summary:        Jakarta Commons Lang Package
License:        Apache License
Group:          Development/Java
#Vendor:         JPackage Project
#Distribution:   JPackage
URL:            http://jakarta.apache.org/commons/lang.html
Source0:        http://archive.apache.org/dist/jakarta/commons/lang/source/commons-lang-2.1-src.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
%if %{gcj_support}
Requires(post): java-gcj-compat
Requires(postun): java-gcj-compat
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
%endif
BuildRequires:  ant, junit, jpackage-utils >= 0:1.5

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
%setup -q -n %{short_name}-%{version}


%build
%ant \
  -Djunit.jar=$(find-jar junit) \
  -Dfinal.name=%{short_name} \
  -Djdk.javadoc=%{_javadocdir}/java \
%if %{build_tests}
  test \
%endif
  dist


%install
rm -rf $RPM_BUILD_ROOT
# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p dist/%{short_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

%{__perl} -pi -e 's/\r$//g' *.html *.txt

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif



%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}


%files
%defattr(0644,root,root,0755)
%doc PROPOSAL.html STATUS.html LICENSE.txt NOTICE.txt RELEASE-NOTES.txt
%{_javadir}/*
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif


%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%ghost %doc %{_javadocdir}/%{name}
