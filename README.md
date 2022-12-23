# itestdevenv

Usage:

```

export GIT_ITO_TOKEN= #https://git-ito.spirenteng.com/-/profile/personal_access_tokens
export JENKINS_ITEST_TOKEN= #https://jenkins-itest.spirenteng.com/jenkins/user/<user>/configure

git clone git@github.com:basilevs/itestdevenv.git
python3 -m pip install -e ./itestdevenv

cd ~/git/itest

python3 -i -m itestdevenv.env
> build_branch() # merge upstream and build current branch
> build_branch('task/ITEST-22122--autoversion') # merge upstream and build remote branch
> download_itest('itest--branches', 6348) # download and configure iTest product, from a given build
```
