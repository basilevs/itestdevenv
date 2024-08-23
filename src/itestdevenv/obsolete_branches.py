from os import environ
from re import compile
from datetime import date, timedelta, datetime 
from urllib.parse import quote 

from gitlab import Gitlab  # python-gitlab package
from jira import JIRA # jira package
from concurrent.futures.thread import ThreadPoolExecutor

# private token can be obtained at https://git-ito.spirenteng.com/-/profile/personal_access_tokens
gitlab = Gitlab('https://git.spirent.io', private_token=environ['GIT_ITO_TOKEN'])

jira_options = {'server': 'https://jira.spirenteng.com/'}
jira = JIRA(options=jira_options, token_auth=environ['JIRA_TOKEN'])

itest_project = gitlab.projects.get(186)

jira_projects = ['ITEST', 'NDA', 'NDO', 'RM', 'NDO', 'INT', 'ENGOP']

jira_issue_patterns = [ compile(i + r'-\d+') for i in jira_projects]



def extract_jira_issues_from_str(input:str):
    for i in jira_issue_patterns:
        pos = 0
        while pos < len(input):
            result = i.search(input, pos=pos)
            if not result:
                break
            yield result.group(0)
            pos = result.endpos

def extract_jira_issues(branch):
    result = []
    result.extend(extract_jira_issues_from_str(branch.name))
    commit = branch.attributes['commit']
    result.extend(extract_jira_issues_from_str(commit['title']))
    for mr in itest_project.commits.get(commit['id']).merge_requests():
        result.extend(extract_jira_issues_from_str(mr['title']))
    return set([i for i in result if i])

def parse_date(iso_datetime):
    """ '2018-05-16T03:34:47.000+00:00' -> date """
    return date.fromisoformat(iso_datetime.split('T')[0])


cutoff_date = (datetime.today() + timedelta(days=-365)).date() 


#https://git-ito.spirenteng.com/itest/itest/-/branches?state=all&search=ITEST-20059--restVersion
compare_url_prefix = itest_project.web_url + '/-/branches?state=all&search='

branch_name_patterns = ['task/', 'bug/', 'cherry-pick', 'defect/', 'qfix/', 'revert-']
branch_name_patterns.extend(['story/'])

def is_eligible_branch_name(branch_name):
    for i in branch_name_patterns :
        if i in branch_name:
            return True
    return False


def fetch_branch_metadata(branch):
    branch.jira_issues = extract_jira_issues(branch)
    for issue in branch.jira_issues:
        if not jira.issue(issue, fields='resolution').fields.resolution:
            return None # never consider unresolved JIRA issues
    commit = branch.attributes['commit']
    branch.author = commit['author_email']
    branch.merge_requests = itest_project.commits.get(commit['id']).merge_requests()
    return branch

def format_merge_request(merge_request):
    return f"[{merge_request['title']}|{merge_request['web_url']}]"

def main():
    with ThreadPoolExecutor(max_workers=100) as executor:
        all_branches = itest_project.branches.list(all=True)
        old_branches = [i for i in all_branches if parse_date(i.attributes['commit']['committed_date']) < cutoff_date]
        filtered_branches = [i for i in old_branches if is_eligible_branch_name(i.name)]
        #filtered_branches = old_branches
        resolved_branches = []

        futures = [executor.submit(fetch_branch_metadata, i) for i in filtered_branches]
        for i in futures:
            branch = i.result() 
            if not branch:
                continue
            resolved_branches.append(branch)
            print('[' + branch.name,'|', compare_url_prefix + quote(branch.name.encode('utf-8')),']', *branch.jira_issues, branch.author, *map(format_merge_request, branch.merge_requests))
            #branch.delete()
        print(len(resolved_branches))

if __name__ == '__main__':
    main()

