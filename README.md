RpmGrill
========

Contribution Guideline
-----------------------
There are two ways to contribute - the *prefered* [gerrithub workflow] or the
github pull requests.

### Gerrithub Workflow ###

We use [gerrithub] for our code reviews and it will be great if you followed
the same process for contributions. This allows us to track code review comments
and how it is addressed in subsequent patches effortlessly. There is also a CI
that monitors gerrit events and runs tests against the patchset in review.

Please sign up with [gerrithub] and your github credentials to make submissions.
Additional permissions on the project will need to be done on a per-user basis.

NOTE: When you set up your account on [gerrithub], it is not necessary to import
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

### How pull requests are dealt with ###

In the case we receive a git pull request, in order to keep the workflow same
for everyone, one of the developers will `cherry-pick -x` your commit and push
it to [gerrithub rpmgrill repo] for review.

Any review comments will be then be communicated back in the pull request
comments so that it can be addressed by the original author. It would be really
helpful to us at this stage if you choose to use the [Gerrithub
workflow](.#gerrihub-workflow).


[gerrithub]: https://review.gerrithub.io "gerrit hub"
[gerrit workflow]: http://www.vogella.com/tutorials/Gerrit/article.html "gerrit workflow"
[gerrithub repo]: https://review.gerrithub.io/#/q/project:default-to-open/rpmgrill "gerrit workflow"

