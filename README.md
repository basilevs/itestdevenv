# itestdevenv

Usage:

```

export GIT_ITO_TOKEN=
export JENKINS_ITEST_TOKEN=
export PYTHONPATH=..../git/itestdevenv/src/

cd ~/git/itest

python3 -i -m itestdevenv.env
> build_branch() # merge upstream and build current branch
> build_branch('task/ITEST-22122--autoversion') # merge upstream and build remote branch
> download_build('itest--branches', 6348) # download and configure iTest product, from a given build
```
