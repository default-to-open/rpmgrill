%pre
# Chose 'pegasus' because the uid and gid differ, and that's confusing
useradd -s /sbin/nologin -d /home/pegasus pegasus >&/dev/null
