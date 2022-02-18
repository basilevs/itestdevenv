from os import environ
from re import compile
from datetime import date, timedelta, datetime 
from urllib.parse import quote 

from gitlab import Gitlab  # python-gitlab package
from jira import JIRA # jira package
from concurrent.futures.thread import ThreadPoolExecutor

# private token can be obtained at https://git-ito.spirenteng.com/-/profile/personal_access_tokens
gitlab = Gitlab('https://git-ito.spirenteng.com', private_token=environ['GIT_ITO_TOKEN'])

jira_options = {'server': 'https://jira.spirenteng.com/'}
jira = JIRA(options=jira_options, token_auth=environ['JIRA_TOKEN'])

itest_project = gitlab.projects.get(186)

jira_projects = ['ITEST', 'NDA', 'NDO', 'RM', 'NDO', 'INT', 'ENGOP']

jira_issue_patterns = [ compile(i + '-\d+') for i in jira_projects]



def extract_jira_issue_from_str(input:str):
    for i in jira_issue_patterns:
        result = i.search(input)
        if result:
            return result.group(0)

def extract_jira_issue(branch):
    result = extract_jira_issue_from_str(branch.name)
    if result:
        return result
    return extract_jira_issue_from_str(branch.attributes['commit']['title'])

def parse_date(iso_datetime):
    """ '2018-05-16T03:34:47.000+00:00' -> date """
    return date.fromisoformat(iso_datetime.split('T')[0])


cutoff_date = (datetime.today() + timedelta(days=-365)).date() 


compare_url_prefix = itest_project.web_url + '/-/compare/v9.0.0...'

branches = itest_project.branches.list(all=True)
branches = [i for i in branches if not i.attributes['protected']]
branches = [i for i in branches if parse_date(i.attributes['commit']['committed_date']) > cutoff_date]
branches = [i for i in branches if 'Gulevich' in i.attributes['commit']['author_name']]
#branches = [i for i in branches if 'task/' in i.name or 'bug/' in i.name or 'cherry-pick' in i.name]
resolved_branches = []

def fetch_jira_issue(branch):
    branch.jira_issue = extract_jira_issue(branch)
    branch.jira_resolution = jira.issue(branch.jira_issue, fields='resolution').fields.resolution if branch.jira_issue else None
    return branch

with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(fetch_jira_issue, i) for i in branches]
    for i in futures:
        branch = i.result() 
        if not branch.jira_issue or branch.jira_resolution:
            resolved_branches.append(branch)
            print('[' + branch.name,'|', compare_url_prefix + quote(branch.name.encode('utf-8')),']', branch.attributes['commit']['author_name'],  branch.jira_issue, branch.jira_resolution)
    print(len(resolved_branches))
