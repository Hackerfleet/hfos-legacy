"""
Exports issues from a list of repositories to individual csv files.
Uses basic authentication (Github username + password) to retrieve issues
from a repository that username has access to. Supports Github API v3.
Forked from: unbracketed/export_repo_issues_to_csv.py
"""
import click
import requests

from hfos.logger import hfoslog, debug, error
from hfos.misc import std_uuid


def log(*args, **kwargs):
    kwargs.update({'emitter': 'GHIMPORT', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


@click.command()
@click.argument('repository')
@click.option('--all', default=False, help='Import open and closed issues')
@click.option('--owner')
@click.option('--project')
@click.option('--ignore-labels', is_flag=True, default=False)
@click.option('--no-tags', is_flag=True, default=False)
@click.option('--username', prompt=True)
@click.password_option()
@click.pass_context
def GithubImporter(ctx, repository, all, owner, project, ignore_labels, no_tags, username, password):
    """Project Importer for Github Repository Issues

    Argument REPOSITORY must be given as 'username/repository'

    Owner and project have to be UUIDs
    """

    db = ctx.obj['db']

    if project is not None:
        project_obj = db.objectmodels['project'].find_one({'uuid': project})

        if project_obj is None:
            project_obj = db.objectmodels['project'].find_one({'name': project})

        if project_obj is None:
            log('Project not found.', lvl=error)
            return
        else:
            project_uuid = project_obj.uuid
    else:
        project_uuid = None

    tags = {}
    if not ignore_labels:
        for tag in db.objectmodels['tag'].find():
            tags[tag.name.lower()] = tag

    def write_issue(issue):
        """Stores a single github issue as task"""

        if 'pull_request' not in issue:

            issue_tags = []
            if not ignore_labels:
                for l in issue['labels']:
                    if l['name'].lower() not in tags:
                        initial = {
                            'uuid': std_uuid(),
                            'name': l['name']
                        }
                        new_tag = db.objectmodels['tag'](initial)
                        new_tag.save()

                        tags[new_tag.name] = new_tag

                        issue_tags.append(new_tag.uuid)
                    else:
                        issue_tags.append(tags[l['name'].lower()].uuid)

            date = issue['created_at'].split('T')[0]

            initial = {
                'uuid': std_uuid(),
                'name': issue['title'],
                'notes': str(issue['state']) + "\n\n" + issue['html_url'],
                'created': date,
                'project': project_uuid
            }
            if len(issue_tags) > 0:
                initial['tags'] = issue_tags

            task = db.objectmodels['task'](initial)
            task.save()
        else:
            log('Pull request issue:', issue, lvl=debug)

    def write_issues(r):
        """Parses JSON response and stores all issues."""

        if r.status_code != 200:
            raise Exception(r.status_code)
        for issue in r.json():
            write_issue(issue)

    def get_issues(name, state, auth):
        """Requests issues from GitHub API"""

        url = 'https://api.github.com/repos/{}/issues?state={}'.format(name, state)
        r = requests.get(url, auth=auth)

        write_issues(r)

        # Multiple requests are required if response is paged
        if 'link' in r.headers:
            pages = {rel[6:-1]: url[url.index('<') + 1:-1] for url, rel in
                     (link.split(';') for link in
                      r.headers['link'].split(','))}
            while 'last' in pages and 'next' in pages:
                pages = {rel[6:-1]: url[url.index('<') + 1:-1] for url, rel in
                         (link.split(';') for link in
                          r.headers['link'].split(','))}
                r = requests.get(pages['next'], auth=auth)
                write_issues(r)
                if pages['next'] == pages['last']:
                    break

    # username = input("Username for 'https://github.com': ")
    # password = getpass("Password for 'https://{}@github.com': ".format(username))
    # auth = (username, password)
    # for repository in args.repositories:
    #    get_issues(repository)

    if all:
        state = 'all'
    else:
        state = 'open'

    auth = (username, password)

    get_issues(repository, state, auth)
