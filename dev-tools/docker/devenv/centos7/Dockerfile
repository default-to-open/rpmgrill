FROM rpmgrill_centos7:latest
MAINTAINER rpmdiff-maint@redhat.com

USER root

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
        perl-Test-Exception perl-File-Fetch perl-List-AllUtils && \
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
