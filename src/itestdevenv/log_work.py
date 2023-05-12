from jira import JIRA # jira package
from os import environ

jira_options = {'server': 'https://jira.spirenteng.com/'}
jira = JIRA(options=jira_options, token_auth=environ['JIRA_TOKEN'])

def get_yesterday_work_logs_for_current_user():
	return jira.worklogs(jql_str='worklogAuthor = currentUser() and worklogDate = -1d')

get_yesterday_work_logs_for_current_user()