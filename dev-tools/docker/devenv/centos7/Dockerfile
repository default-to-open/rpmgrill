FROM centos:7
MAINTAINER rpmdiff-maint@redhat.com

### code ###
VOLUME ["/project"]
VOLUME ["/code"]

### setup installs /usr/share/doc/setup-*/uidgid  ###
### need by rpmgrill so ensure docs are installed ###

RUN cp /etc/yum.conf /tmp/ && \
    sed -e 's|\(.*tsflags.*\)nodocs\(.*\)|\1\2|' -i /etc/yum.conf && \
    yum install -y setup && \
    yum -y clean all && \
    cp /tmp/yum.conf /etc/

### create dev user(1000) with sudo ###
RUN yum install -y zsh sudo less initscripts && \
    useradd -u 1000 dev && \
    usermod -aG wheel dev  && \
    echo 'dev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo  'kernel.core_pattern=core' >> /etc/sysctl.conf && \
    chown dev:dev /code /project


### Use epel for additional dependencies
RUN yum install -y epel-release

### minimal developer tools ###
RUN yum -y install \
        git vim  && \
    yum -y clean all

### git config ###
ADD gitconfig /etc/gitconfig

### test dependencies ###

RUN yum install -y \
        tar bzip2 desktop-file-utils rpm-build redhat-rpm-config \
        clamav clamav-data elfutils koji git libxslt \
        perl-Test-Harness perl-Test-Perl-Critic perl-HTML-Parser \
        perl-XML-Simple perl-JSON-XS perl-YAML \
        perl-Test-Differences  perl-IPC-Run perl-Sort-Versions \
        perl-Digest-SHA1 perl-File-Slurp perl-Test-LongString \
        perl-Time-ParseDate perl-YAML-Syck perl-Time-Piece \
        perl-CGI perl-Test-Deep  perl-Module-Build perl-Net-DNS \
        perl-Pod-POM perl-Test-MockObject perl-XMLRPC-Lite \
        perl-Test-Exception perl-File-Fetch && \
    yum -y clean all

### missing dependencies not package as RPMs (yet)
### adding a few more dependencies to install File::LibMagic
RUN yum install -y \
        perl-App-cpanminus file-libs gcc file-devel && \
    yum -y clean all

RUN cpanm install File::LibMagic

USER dev
WORKDIR /code
CMD  bash
