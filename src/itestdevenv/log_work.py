from os import environ
from pprint import pprint
from operator import itemgetter
from itertools import groupby

from datetime import datetime, timedelta

from jira import JIRA, JIRAError  # jira package
from toggl.api_client import TogglClientApi

jira_options = {'server': 'https://jira.spirenteng.com/'}
jira = JIRA(options=jira_options, token_auth=environ['JIRA_TOKEN'])


def _is_work_logged(interval):
    return bool(jira.search_issues(jql_str=f'worklogAuthor = currentUser() AND worklogDate = startOfDay({interval})', maxResults=1))


def _is_work_logged_yesterday():
    return _is_work_logged('-1d')

def jira_key_exists(key):
	try:
		return bool(jira.issue(key))
	except JIRAError:
		return False

if _is_work_logged_yesterday():
	print('Work logged yesterday')
	quit(1)


settings = {
    'token': environ['TOGGL_TOKEN'],
    'user_agent': 'basilevs jira export',
    'workspace_id': 1528494
}
toggle_client = TogglClientApi(settings)

yesterday = datetime.now() - timedelta(days=1)
report = toggle_client.get_project_times(155737388, yesterday, yesterday)

data = report['data']
get_description = itemgetter('description')
data.sort(key=get_description)

description_to_time = {}
for description, entries in groupby(data, key=get_description):
    description_to_time[description] = timedelta(milliseconds=sum(i['dur'] for i in entries))


def description_to_jira_key(description):
    key = description.split()[0]
    if not jira_key_exists(key):
        raise ValueError(f'Jira key {description} does not exist')
    return key

result = {}

for description, time in description_to_time.items():
	key = description_to_jira_key(description)
	result[key] = time

for key, time in result.items():
	jira.add_worklog(issue=key, timeSpentSeconds=time.total_seconds(), started=yesterday, comment='Toggl Track automated conversion')

pprint(result)
pprint(len(result))
