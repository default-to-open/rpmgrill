RpmGrill
========

Contribution Guideline
-----------------------
There are two ways to contribute - the *prefered* [gerrithub workflow] or the
[pull requests].

### Gerrithub Workflow ###

We use [gerrithub project] for our code reviews and it will be great if you
followed the same process for contributions. [gerrit] allows us to do
code reviews and track how  comments are addressed in subsequent patches
effortlessly. There is also a CI that monitors gerrit events and runs tests
against the patchset in review.

Please sign up with [gerrithub] and your github credentials to make submissions.
Additional permissions on the project will need to be done on a per-user basis.

NOTE: When you set up your account on [gerrithub], it is not necessary to import
your existing rpmgrill fork.

Install `git-review` to make code reviews easier.
```
    yum install -y git-review
```

#### Set up your repo for gerrit ####

Add a new remote to your working tree:

    git remote add gerrit ssh://<username>@review.gerrithub.io:29418/default-to-open/rpmgrill

Replace `<username>` with your gerrithub username.

Now run:

    git review -s
    scp -p -P 29418 <username>@review.gerrithub.io:hooks/commit-msg \
        `git rev-parse --git-dir`/hooks/commit-msg

Again, replace `<username>` with your gerrithub username.

### GitHub pull requests  ###

In the case we receive a git pull request, in order to keep the workflow same
for everyone, one of the developers will `cherry-pick -x` your commit and push
it to [gerrithub project] for review.

Any review comments will be then be communicated back in the pull request
comments so that it can be addressed by the original author. It would be really
helpful to us if at this stage you choose to use the preferred
[gerrithub workflow].

[gerrithub]: https://review.gerrithub.io "gerrit hub"
[gerrithub project]: https://review.gerrithub.io/#/q/project:default-to-open/rpmgrill "gerrit workflow"
[gerrithub workflow]: #gerrithub-workflow "Gerrithub Workflow"
[pull requests]: #github-pull-requests "Github pull requests"
[gerrit]: http://www.vogella.com/tutorials/Gerrit/article.html "gerrit workflow"
