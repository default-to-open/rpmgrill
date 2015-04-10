RpmGrill
========

Contribution Guideline
-----------------------

We use [gerrit hub] for code reviews and thus github pull requests will not be
looked at. Code submissions should be done via [gerrit hub]. This allows us to
track code review comments and how it is addressed in subsequent patches
effortlessly.

Please sign up with [gerrit hub] and your github credentials to make
submissions. Additional permissions on the project will need to be done
on a per-user basis.

NOTE: When you set up your account on [gerrit hub], it is not necessary to import
your existing rpmgrill fork.


Install `git-review` to make code reviews easier.
```
    yum install -y git-review
```

### Set up your repo for gerrit ###

Add a new remote to your working tree:

    git remote add gerrit ssh://<username>@review.gerrithub.io:29418/default-to-open/rpmgrill

Replace `<username>` with your gerrithub username.

Now run:

    git review -s
    scp -p -P 29418 username@review.gerrithub.io:hooks/commit-msg `git rev-parse --git-dir`/hooks/commit-msg

Again, replace `<username>` with your gerrithub username.

[gerrit hub]: https://review.gerrithub.io "gerrit hub"
