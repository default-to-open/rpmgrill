RpmGrill
========

Contribution Guideline
-----------------------
There are two ways to contribute - the **prefered** [gerrithub workflow] or the
[pull requests].

### Gerrithub Workflow ###

We use [gerrithub project] for our code reviews and it will be great if you
followed the same process for contributions. [gerrit] allows us to do
code reviews and track how comments are addressed in subsequent patches
effortlessly. There is also a Jenkins that monitors gerrit events and
runs tests against the patchset in review.

Please sign up with [gerrithub] and your github credentials to make submissions.
Additional permissions on the project will need to be done on a per-user basis.

NOTE: When you set up your account on [gerrithub], it is not necessary to import
your existing rpmgrill fork.

#### Set up your repo for gerrit ####

Add a new remote to your local repo:
```
    git remote add gerrit ssh://<username>@review.gerrithub.io:29418/default-to-open/rpmgrill.git

    scp -p -P 29418 <username>@review.gerrithub.io:hooks/commit-msg \
        `git rev-parse --git-dir`/hooks/commit-msg

```

**NOTE** Replace `<username>` with your gerrithub username.

##### TIP: install [git-review] to make code reviews easier #####

``` yum install -y git-review ```

Now run:

    git review -s


##### TIP: simplify gerrit repo url #####

Consider making use of `~/.ssh/config` to setup `gerrithub` host as below

```
Host gerrithub
    HostName gerrithub.io
    Port 29418
    User <username>
    IdentityFile <path/to/your/private-gerrithub-key.file>
```

This allows you to clone `git clone gerrithub:default-to-open/rpmgrill.git` or
`git remote add gerrit gerrithub:default-to-open/rpmgrill.git`


#### submitting changes ####
Submitting changes usually only invokes something like:

```
    git fetch gerrit
    git checkout -b my-cool-feature  gerrit/develop
    # hack hack hack
    git commit -a

    # submit changes
    git push gerrit HEAD:refs/for/develop
```

### GitHub pull requests  ###

In the case we receive contributions as pull requests, in order to keep the
workflow same for everyone, one of the developers will `cherry-pick -x` the
commit and push it to [gerrithub project] for review.

Any review comments made in gerrit will be then be communicated back manually
in the pull request comments so that it can be addressed by the original author.
It would be really helpful to us if at this stage you choose to use the preferred
[gerrithub workflow] since it makes the review and testing process a lot easier
otherwise we would have to repeat the same exercise which is a bit cumbersome
for all of us.


[gerrithub workflow]: #gerrithub-workflow "Gerrithub Workflow"
[pull requests]: #github-pull-requests "Github pull requests"

[gerrithub]: https://review.gerrithub.io "gerrit hub"
[gerrithub project]: https://review.gerrithub.io/#/q/project:default-to-open/rpmgrill "gerrithub project"
[gerrit]: https://review.gerrithub.io/Documentation/intro-quick.html "Gerrit"
[git-review]: https://www.mediawiki.org/wiki/Gerrit/git-review "git-review"
