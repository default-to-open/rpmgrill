FROM fedora:20
MAINTAINER rpmdiff-maint@redhat.com

### code ###
VOLUME ["/project"]
VOLUME ["/code"]

RUN yum install -y deltarpm && yum clean all

### setup installs /usr/share/doc/setup-*/uidgid  ###
### need by rpmgrill so ensure docs are installed ###
RUN cp /etc/yum.conf /tmp/ && \
    sed -e 's|\(.*tsflags.*\)nodocs\(.*\)|\1\2|' -i /etc/yum.conf && \
    yum install -y setup && \
    yum -y clean all

### create dev user(1000) with sudo ###
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


USER dev
WORKDIR /code
CMD  bash
