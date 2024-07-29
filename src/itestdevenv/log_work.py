from os import environ
from pprint import pprint
from operator import itemgetter
from itertools import groupby
from re import compile

from datetime import datetime, timedelta
from dateutil.parser import parse
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
toggl_project_id = 155737388


def _is_work_logged(day: datetime) -> bool:
	# YYYY-MM-DD
	interval = day.strftime('%Y-%m-%d')
	return bool(jira.search_issues(jql_str=f'worklogAuthor = currentUser() AND worklogDate = "{interval}"', maxResults=1))

def work_logged_since(day: datetime) -> float:
	# YYYY-MM-DD
	result = jira.search_issues(jql_str=f'worklogAuthor = currentUser() AND worklogDate >= "{day.strftime("%Y-%m-%d")}"', maxResults=1000)
	if result.total != len(result):
		raise ValueError(f"Received {len(result)}, expected: {result.total}")
	user = jira.session().name
	start_date = day.astimezone()
	seconds = 0
	for issue in result:
		for worklog in jira.worklogs(issue):
			if worklog.author.key == user:
				started = parse(worklog.started)
				if started > start_date:
					seconds = seconds + worklog.timeSpentSeconds
	return float(seconds) / 3600

def work_logged_this_month():
	date = datetime.now()
	month_start = datetime(year=date.year, month=date.month, day=1)
	return work_logged_since(month_start)

def toggl_for_interval(start:datetime, stop:datetime) -> Dict[str, timedelta]:
	report = toggle_client.get_project_times(toggl_project_id, start, stop)
	try:
		if int(report['total_count']) > int(report['per_page']):
			raise ValueError('Too many entries')
		data = report['data']
		get_description = itemgetter('description')
		data.sort(key=get_description)

		description_to_time = {}
		for description, entries in groupby(data, key=get_description):
			description_to_time[description] = timedelta(
				milliseconds=sum(i['dur'] for i in entries))
		return description_to_time
	except KeyError:
		pprint(report)
		raise


def find_subtask(key, summary) -> Optional[Issue]:
	for issue in jira.search_issues(f'parent = {key} AND summary ~ "{summary}"'):
		return issue
	return None


def find_review_subtask(key):
	return find_subtask(key, 'Code Review')

def find_review_in_parent(issue: Issue):
	try:
		parent = issue.fields.parent
	except AttributeError:
		return None
	subtask = find_review_subtask(parent.key)
	if subtask:
		return subtask
	return find_review_in_parent(parent)


def review_for_jira_key(key):
	issue = jira.issue(key)
	if not issue:
		raise ValueError(f'Jira key {key} does not exist')
	subtask = find_review_subtask(key)
	if subtask:
		return subtask
	subtask = find_review_in_parent(issue)
	if subtask:
		return subtask
	return issue


mr_description_pattern = compile(r'^MR\d+:: (?:Draft: )?\[(\w+-\d+)\].*')


def worklog_to_issue(description):
	try:
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
	except:
		raise ValueError(f'Could not parse description: {description}')


def human_readable(duration: timedelta) -> str:
	totsec = duration.total_seconds()
	h = int(totsec//3600)
	m = int((totsec - h*3600)/60)
	return f'{h}:{m}'


def worked_issues(start:datetime, stop:datetime) -> Dict[Issue, timedelta]:
	result = {}
	for description, time in toggl_for_interval(start, stop).items():
		issue = worklog_to_issue(description)
		if time > timedelta(minutes=1):
			result[issue] = result.get(issue, timedelta()) + time
			print(f'{issue.key:<11} {description:<100} {human_readable(time)}')
	print("Entries count:", len(result))
	print("Total time:", human_readable(sum(result.values(), timedelta())))
	return result


def log_work_for_day(day: datetime):
	if _is_work_logged(day):
		raise ValueError(f'Work logged on {day.strftime("%Y-%m-%d %A")}')

	for issue, time in worked_issues(day, day).items():
		jira.add_worklog(issue=issue, timeSpentSeconds=time.total_seconds(
		), started=day, comment='dev')


def test_day(day):
	print('Testing day:', day.strftime('%Y-%m-%d %A'))
	print('Logged:', _is_work_logged(day))
	worked_issues(day, day)


def test_days_ago(days):
	day = datetime.now() - timedelta(days=days)
	test_day(day)
	
def test_since(day):
	print('Testing since:', day.strftime('%Y-%m-%d %A'))
	worked_issues(day, datetime.now())

def log_days_ago(days):
	day = datetime.now() - timedelta(days=days)
	log_work_for_day(day)

#log_days_ago(1) #yesterday
#log_days_ago(2)
#log_days_ago(7) #yesterday
#test_days_ago(3)
#log_work_for_day(datetime(2023, 5, 19))
#test_day(yesterday)
#test_since(datetime.now() - timedelta(days=7))
#test_since(datetime.now() - timedelta(days=14))
#test_since(yesterday)
