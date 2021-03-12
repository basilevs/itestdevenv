from os import environ

from jenkins import Jenkins
from git import Git
from jenkins_util import build_branch

git = Git()

branch = git.current_branch()

jenkins = Jenkins('https://jenkins-itest.spirenteng.com/jenkins/', username='vgulevich',
                  password=environ['JENKINS_TOKEN'])

version = '8.5.0'
git.update_branch(branch, 'v' + version)

print(build_branch(jenkins, branch, installers=True, test=True, version=version))
