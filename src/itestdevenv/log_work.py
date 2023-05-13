from os import environ
from pprint import pprint
from operator import itemgetter
from itertools import groupby
from re import compile

from datetime import datetime, timedelta
from typing import Optional, Dict

from jira import JIRA, Issue, JIRAError  # jira package
from toggl.api_client import TogglClientApi

jira_options = {'server': 'https://jira.spirenteng.com/'}
jira = JIRA(options=jira_options, token_auth=environ['JIRA_TOKEN'])

settings = {
    'token': environ['TOGGL_TOKEN'],
    'user_agent': 'basilevs jira export',
    'workspace_id': 1528494
}
toggle_client = TogglClientApi(settings)

def _is_work_logged(day: datetime) -> bool:
    # YYYY-MM-DD
    interval = day.strftime('%Y-%m-%d')
    return bool(jira.search_issues(jql_str=f'worklogAuthor = currentUser() AND worklogDate = "{interval}"', maxResults=1))


def toggl_for_day(day) -> Dict[str, timedelta]:
    report = toggle_client.get_project_times(155737388, day, day)

    data = report['data']
    get_description = itemgetter('description')
    data.sort(key=get_description)

    description_to_time = {}
    for description, entries in groupby(data, key=get_description):
        description_to_time[description] = timedelta(
            milliseconds=sum(i['dur'] for i in entries))
    return description_to_time


def find_subtask(key, summary) -> Optional[Issue]:
    for issue in jira.search_issues(f'parent = {key} AND summary ~ "{summary}"'):
        return issue
    return None


def get_parent(key):
    return jira.issue(key).fields.parent


def review_for_jira_key(key):
    issue = jira.issue(key)
    if not issue:
        raise ValueError(f'Jira key {key} does not exist')
    subtask = find_subtask(key, 'Code Review')
    if subtask:
        return subtask
    parent = issue.fields.parent
    if parent:
        return review_for_jira_key(parent.key)
    raise ValueError(f'No code review subtask for {key}')


mr_description_pattern = compile(r'^MR\d+:: \[(\w+-\d+)\].*')


def worklog_to_issue(description):
    # check for MR
    match = mr_description_pattern.match(description)
    if match:
        key = match.group(1)
        return review_for_jira_key(key)
    key = description.split()[0]
    result = jira.issue(key)
    if not result:
        raise ValueError(f'Jira key {key} does not exist')
    return result


def human_readable(duration: timedelta) -> str:
    totsec = duration.total_seconds()
    h = int(totsec//3600)
    m = int((totsec - h*3600)/60)
    return f'{h}:{m}'


def worked_issues(day):
	result = {}
	for description, time in toggl_for_day(day).items():
		issue = worklog_to_issue(description)
		if time > timedelta(minutes=1):
			result[issue] = time
			print(f'{issue.key:<11} {description:<100} {human_readable(time)}')
	print("Entries count:", len(result))
	print("Total time:", human_readable(sum(result.values(), timedelta())))
	return result


def log_work_for_day(day):
    if _is_work_logged(day):
        raise ValueError(f'Work logged on {day.strftime("%Y-%m-%d %A")}')

    for issue, time in worked_issues(day).items():
        jira.add_worklog(issue=issue, timeSpentSeconds=time.total_seconds(
        ), started=yesterday, comment='Toggl Track automated conversion')


def test_day(day):
    print('Testing day:', day.strftime('%Y-%m-%d %A'))
    print('Logged:', _is_work_logged(day))
    worked_issues(day)


def test_days_ago(days):
    day = datetime.now() - timedelta(days=days)
    test_day(day)


yesterday = datetime.now() - timedelta(days=1)
log_work_for_day(yesterday)
#test_days_ago(3)
