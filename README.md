RpmGrill
========

Contribution Guideline
-----------------------

We use [gerrit hub](https://review.gerrithub.io). for code reviews and thus
pull requests will not be looked at on github. Code submissions should be done
via [gerrit hub].

Please sign up with https://www.gerrithub.io and your github credentials to
make submissions. Additional permissions on the project will need to be done
on a per-user basis.

When you set up your account on gerrithub.io, it is not necessary to import
your existing rpmgrill fork.

```shell
    yum install git-review
```

To set up your repo for gerrit:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a new remote to your working tree:

    git remote add gerrit ssh://<username>@review.gerrithub.io:29418/default-to-open/rpmgrill

Replace `<username>` with your gerrithub username.

Now run:

    git review -s
    scp -p -P 29418 username@review.gerrithub.io:hooks/commit-msg `git rev-parse --git-dir`/hooks/commit-msg

Again, replace `<username>` with your gerrithub username.

