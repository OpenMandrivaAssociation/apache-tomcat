Name:		apache-tomcat
Version:	11.0.27
Release:	1
Summary:	Java Servlet 6.1 and JSP 4.0 container
Group:		System/Servers
License:	ASL 2.0
URL:		https://tomcat.apache.org/
Source0:	https://dlcdn.apache.org/tomcat/tomcat-11/v%{version}/src/apache-tomcat-%{version}-src.tar.gz

BuildArch:	noarch
BuildRequires:	ant
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.eclipse.jdt:ecj)
BuildRequires:	mvn(org.apache.tomcat:jakartaee-migration)
BuildRequires:	mvn(commons-daemon:commons-daemon)
BuildRequires:	mvn(org.apache.bcel:bcel)
BuildRequires:	mvn(org.apache.commons:commons-compress)
BuildRequires:	mvn(commons-io:commons-io)
BuildRequires:	mvn(commons-codec:commons-codec)
BuildRequires:	mvn(org.apache.commons:commons-lang3)
BuildRequires:	mvn(org.tukaani:xz)
BuildSystem:	ant

%description
Apache Tomcat 11 implements the Jakarta Servlet 6.1, Pages 4.0, Expression
Language 6.0, WebSocket 2.2, and Authentication 3.1 specifications. It is
built from source with the system Ant, the system Eclipse compiler, and
system jars. The upstream build's download of prebuilt dependencies is
turned off.

%prep
%setup -q -n apache-tomcat-%{version}-src
mkdir -p bnd-stub/aQute/bnd/annotation/spi bnd-stub/classes
cat > bnd-stub/aQute/bnd/annotation/spi/ServiceConsumer.java << 'END'
package aQute.bnd.annotation.spi;
@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.CLASS)
@java.lang.annotation.Target({java.lang.annotation.ElementType.TYPE, java.lang.annotation.ElementType.PACKAGE})
public @interface ServiceConsumer {
    Class<?> value();
}
END
cat > bnd-stub/aQute/bnd/annotation/spi/ServiceProvider.java << 'END'
package aQute.bnd.annotation.spi;
@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.CLASS)
@java.lang.annotation.Target({java.lang.annotation.ElementType.TYPE, java.lang.annotation.ElementType.PACKAGE})
public @interface ServiceProvider {
    Class<?> value();
}
END
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
"$JAVA_HOME/bin/javac" -d bnd-stub/classes bnd-stub/aQute/bnd/annotation/spi/ServiceConsumer.java bnd-stub/aQute/bnd/annotation/spi/ServiceProvider.java
"$JAVA_HOME/bin/jar" --create --file bnd-stub/bnd-stub.jar -C bnd-stub/classes .
# The mvn() BuildRequires install these jars into %{_javadir}.
javadir="%{_javadir}"
echo "$javadir" > .tomcat-javadir
cat > build.properties << EOF
execute.download=false
skip.build.java.version=true
skip.installer=true
jdt.checksum.enabled=false
bnd.checksum.enabled=false
migration-lib.checksum.enabled=false
commons-daemon.bin.checksum.enabled=false
jdt.jar=${javadir}/ecj.jar
bnd.jar=$(pwd)/bnd-stub/bnd-stub.jar
migration-lib.jar=${javadir}/jakartaee-migration.jar
commons-daemon.jar=${javadir}/commons-daemon.jar
EOF

%install
mkdir -p %{buildroot}%{_datadir}/tomcat
cp -a output/build/. %{buildroot}%{_datadir}/tomcat/
javadir="$(cat .tomcat-javadir)"
for jar in bcel commons-compress commons-io commons-codec commons-lang3 xz; do
	cp -p "$javadir/$jar.jar" %{buildroot}%{_datadir}/tomcat/lib/
done

%files
%doc LICENSE NOTICE README.md RELEASE-NOTES
%{_datadir}/tomcat
