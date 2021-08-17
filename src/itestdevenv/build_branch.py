from os import environ
from os.path import join

from jenkins import Jenkins
from .jenkins_util import build_branch as jenkins_build_branch
from gitlab import Gitlab

from .git import Git
from .maven import extract_version, remove_qualifier


gitlab = Gitlab('https://git-ito.spirenteng.com', private_token=environ['GIT_ITO_TOKEN'])

itest_project = gitlab.projects.get(186)

git = Git()


jenkins = Jenkins('https://jenkins-itest.spirenteng.com/jenkins/', username='vgulevich',
                  password=environ['JENKINS_ITEST_TOKEN'])

main_pom = join(git.toplevel(), 'dev', 'src', 'releng', 'com.spirent.itest.releng.parent', 'pom.xml')



def build_branch():
    branch = git.current_branch()
    # branch = 'bug/RM-23112--errorCode'
    version = remove_qualifier(extract_version(main_pom))
    git.update_branch(branch, 'v' + version)
    build_url = jenkins_build_branch(jenkins, branch, docker=True, installers=True, test=True, version=version)
    print(build_url)
    
    for merge in itest_project.mergerequests.list(source_branch=branch):
        if merge.state == 'opened':
            print(merge.web_url)
            merge.notes.create(data={'body': "Started {}".format(build_url)})
