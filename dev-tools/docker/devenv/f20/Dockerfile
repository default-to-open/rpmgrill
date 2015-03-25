FROM fedora:20
MAINTAINER rpmdiff-maint@redhat.com

### code ###
VOLUME ["/project"]
VOLUME ["/code"]

RUN yum install -y deltarpm && yum clean all

### setup installs /usr/share/doc/setup-*/uidgid  ###
### need by rpmgrill so ensure docs are installed ###

### create dev user(1000) with sudo ###
RUN cp /etc/yum.conf /tmp/ && \
    sed -e 's|\(.*tsflags.*\)nodocs\(.*\)|\1\2|' -i /etc/yum.conf && \
    yum install -y setup && \
    yum -y clean all && \
    cp /tmp/yum.conf /etc/

RUN yum install -y zsh sudo less initscripts && \
    useradd -u 1000 dev && \
    usermod -aG wheel dev  && \
    echo 'dev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo  'kernel.core_pattern=core' >> /etc/sysctl.conf && \
    chown dev:dev /code /project


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
        perl-XML-Simple perl-JSON-XS perl-YAML perl-File-LibMagic  \
        perl-Test-Differences  perl-IPC-Run perl-Sort-Versions \
        perl-Digest-SHA1 perl-File-Slurp perl-Test-LongString \
        perl-Time-ParseDate perl-YAML-Syck perl-Time-Piece \
        perl-CGI perl-Test-Deep  perl-Module-Build perl-Net-DNS \
        perl-Pod-POM perl-Test-MockObject perl-SOAP-Lite \
        perl-Test-Exception perl-File-Fetch perl-List-AllUtils \
        perl-Test-MockModule && \
    yum -y clean all


USER dev
WORKDIR /code
CMD  bash
