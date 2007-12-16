%define gcj_support        1
%define base_name       lang
%define short_name      commons-%{base_name}
%define name            jakarta-%{short_name}
%define section         free

%bcond_with             tests

Name:           %{name}
Version:        2.3
Release:        %mkrel 1.0.2
Epoch:          0
Summary:        Jakarta Commons Lang Package
License:        Apache License
Group:          Development/Java
URL:            http://jakarta.apache.org/commons/lang.html
Source0:        http://archive.apache.org/dist/jakarta/commons/lang/source/commons-lang-2.3-src.tar.gz
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        %{short_name}-%{version}-jpp-depmap.xml
Source5:        %{short_name}-%{version}.pom
Source6:        http://archive.apache.org/dist/jakarta/commons/lang/source/commons-lang-2.3-src.tar.gz.md5
Source7:        http://archive.apache.org/dist/jakarta/commons/lang/source/commons-lang-2.3-src.tar.gz.asc
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
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

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


%build
%{ant} \
  -Dfinal.name=%{short_name} \
  -Djdk.javadoc=%{_javadocdir}/java \
%if %with tests
  -Djunit.jar=$(build-classpath junit) \
  test \
%endif
  jar \
  javadoc

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}
%{__cp} -a dist/%{short_name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `echo $jar| %{__sed} "s|jakarta-||g"`; done)
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `echo $jar| %{__sed} "s|-%{version}||g"`; done)

%add_to_maven_depmap %{base_name} %{base_name} %{version} JPP %{name}

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -m 644 %{SOURCE5} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a dist/docs/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%{__perl} -pi -e 's/\r$//g' *.html *.txt

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

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
%doc LICENSE.txt NOTICE.txt RELEASE-NOTES.txt STATUS.html
%{_javadir}/*
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}
