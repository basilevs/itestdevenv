from os import environ

from jenkins import Jenkins
from git import Git
from jenkins_util import build_branch as jenkins_build_branch

from gitlab import Gitlab

gitlab = Gitlab('https://git-ito.spirenteng.com', private_token=environ['GIT_ITO_TOKEN'])

itest_project = gitlab.projects.get(186)

git = Git()


jenkins = Jenkins('https://jenkins-itest.spirenteng.com/jenkins/', username='vgulevich',
                  password=environ['JENKINS_ITEST_TOKEN'])

version = '8.6.0'

def build_branch():
    branch = git.current_branch()
    # branch = 'bug/RM-23112--errorCode'
    git.update_branch(branch, 'v' + version)
    build_url = jenkins_build_branch(jenkins, branch, docker=True, installers=True, test=True, version=version)
    print(build_url)
    
    for merge in itest_project.mergerequests.list(source_branch=branch):
        if merge.state == 'opened':
            print(merge.web_url)
            merge.notes.create(data={'body': "Started {}".format(build_url)})
