FROM fedora:25
MAINTAINER rpmdiff-maint@redhat.com

### setup installs /usr/share/doc/setup-*/uidgid  ###
### need by rpmgrill so ensure docs are installed ###
RUN dnf reinstall -y setup && \
    dnf -y clean all

### test dependencies ###
RUN dnf install -y \
        tar bzip2 desktop-file-utils rpm-build redhat-rpm-config \
        clamav clamav-data elfutils koji git libxslt \
        clamav clamav-data elfutils koji git libxslt perl-Test-Harness \
        perl-Test-Perl-Critic perl-HTML-Parser perl-XML-Simple perl-JSON-XS \
        perl-YAML perl-File-LibMagic perl-Test-Differences  perl-IPC-Run \
        perl-Sort-Versions perl-Digest-SHA1 perl-File-Slurp \
        perl-Test-LongString perl-Time-ParseDate perl-YAML-Syck \
        perl-Time-Piece  perl-CGI perl-Test-Deep perl-Module-Build \
        perl-Net-DNS perl-Pod-POM perl-Test-MockObject perl-XMLRPC-Lite \
        perl-SOAP-Lite perl-Devel-Cover perl-Test-Exception \
        perl-File-Fetch perl-List-AllUtils perl-Test-MockModule \
        perl-open perl-boolean && \
    dnf -y clean all


WORKDIR /code
CMD  bash
