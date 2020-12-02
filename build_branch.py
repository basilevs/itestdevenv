from os import environ

from jenkins import Jenkins
from git import Git
from jenkins_util import build_branch

git = Git()

branch = git.current_branch()

jenkins = Jenkins('https://jenkins-itest.spirenteng.com/jenkins/', username='vgulevich',
                  password=environ['JENKINS_TOKEN'])

git.update_branch(branch)

print(build_branch(jenkins, branch))
