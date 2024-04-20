from os import environ

from jira import JIRA, Issue, JIRAError  # jira package
from jira.client import ResultList
from jira.resources import Issue

jira_options = {'server': 'https://jira.spirenteng.com/'}
jira = JIRA(options=jira_options, token_auth=environ['JIRA_TOKEN'])

base_jql_filter = 'project in ("Velocity iTest", "Network Devops Agent")'

def check_incomplete(results: ResultList):
	if len(results) != results.total:
		raise ValueError(f'Total: {results.total}, received: {len(results)}')
	return results


def find_link_blocked():
	for issue in check_incomplete(jira.search_issues(jql_str=f'{base_jql_filter} AND (issueFunction in hasLinks("is blocked by")) AND resolution = Unresolved', fields=['issuelinks', 'labels'], maxResults=10000)):
		for link in issue.fields.issuelinks:
			if link.type.name != 'Blocks':
				continue
			try:
				link.inwardIssue
			except AttributeError:
				continue
			try:
				if link.inwardIssue.fields.status.statusCategory.key != 'done':
					yield issue
					break
			except AttributeError:
				raise ValueError(str(issue), dir(link))
	return

def find_label_blocked():
	for issue in check_incomplete(jira.search_issues(jql_str=f'{base_jql_filter} AND (issueFunction in hasLinks("is blocked by")) AND labels = blocked', fields=['labels'], maxResults=10000)):
		yield issue
	return

def label_blocked(issue: Issue, is_blocked: bool):
	try:
		labels = list(issue.fields.labels)
	except AttributeError:
		labels = []
	was_blocked = 'blocked' in labels
	if was_blocked != is_blocked:
		print(f'{issue} is blocked: {is_blocked}')
		if is_blocked:
			issue.update(labels=[{"add": 'blocked'}])
		else:
			issue.update(labels=[{"remove": 'blocked'}])

def process_all():
	blocked = list(find_link_blocked())
	for b in blocked:
		label_blocked(b, True)
	for b in find_label_blocked():
		if b not in blocked:
			label_blocked(b, False)

if __name__ == '__main__':
	process_all()
		