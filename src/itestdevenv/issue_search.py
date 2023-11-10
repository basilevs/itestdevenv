# Search for JIRA issues by regular expression

from itertools import chain
from os import environ
from jira import JIRA
from pprint import pprint
from jira.client import ResultList, Comment
from re import compile

jql_parameter = 'text ~ "Container not found"'
regex = compile("Container \\d+ not found")
matcher_parameter = lambda x: bool(regex.search(x))

jira_options = {'server': 'https://jira.spirenteng.com/'}
jira = JIRA(options=jira_options, token_auth=environ['JIRA_TOKEN'])
#issue = jira.issue('NDO-1206')

jira_projects = ['ITEST', 'NDA', 'NDO', 'RM', 'NDO', 'INT', 'ENGOP']
projects_jql = "project in (" + \
    ", ".join([f'"{name}"' for name in jira_projects]) + ")"
jql = f'{projects_jql} AND {jql_parameter}'
issues: ResultList = jira.search_issues(jql_str=jql, maxResults=0, fields="summary,description,comment", expand="")

for issue in issues:    
    data = chain([issue.fields.summary, issue.fields.description], map(lambda x: x.body.replace('\r\n', ' '), issue.fields.comment.comments))
    for text in data:
        if not text:
            continue
        if matcher_parameter(text):
            print(issue.permalink())
            break
    
